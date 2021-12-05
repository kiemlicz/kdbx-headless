from __future__ import annotations

import logging
import os
import threading
import time
from typing import Iterator, Dict

import secretstorage

log = logging.getLogger(__name__)


class KDBXService:
    def get(self, **kwargs) -> Iterator[str]:
        pass


class KDBXProxy(KDBXService):
    """
    Use when the KDBX should be opened not by kdbx-headless process
    """
    Threshold = 15.0  # seconds

    def __init__(self, kdbx: Dict[str, str]):
        self.db_name = kdbx['db_name']
        self._cleanup_task = threading.Timer(KDBXProxy.Threshold, self._close)
        self._last_access = time.time()
        self._dbus_lock = threading.RLock()

    def get(self, **kwargs) -> Iterator[str]:
        with self._dbus_lock:
            connection = self._open()
            self._reschedule()
            try:
                # we could fetch it all and close right here
                secret_service = next(filter(
                    lambda c: c.collection_path == f"/org/freedesktop/secrets/collection/{self.db_name}",
                    secretstorage.get_all_collections(connection)
                ))
                return map(lambda i: i.get_secret().decode("utf-8"), secret_service.search_items({**kwargs}))
            except StopIteration as e:
                self._close()
                msg = f"Cannot find DB: {self.db_name}"
                log.exception(msg)
                raise RuntimeError(msg) from e

    def _open(self):
        log.info("Opening DBUS connection")
        with self._dbus_lock:
            self.connection = secretstorage.dbus_init()
            self._last_access = time.time()
            return self.connection

    def _close(self):
        log.info("Closing DBUS connection")
        with self._dbus_lock:
            if (time.time() - self._last_access) >= KDBXProxy.Threshold:
                self.connection.close()
                log.info("Closed DBUS connection")

    def _reschedule(self):
        try:
            self._cleanup_task.cancel()
            self._cleanup_task = threading.Timer(KDBXProxy.Threshold, self._close)
            self._cleanup_task.start()
            log.debug("Rescheduled connection cleanup")
        except Exception as e:
            log.exception("Cannot reschedule cleanup")
            self._cleanup_task = threading.Timer(KDBXProxy.Threshold, self._close)
            self._cleanup_task.start()


class KDBX(KDBXService):
    def __init__(self, kdbx: Dict[str, str]) -> KDBX:
        # todo implement same closing thread to close the DB after ttl
        c = kdbx.copy()
        c.update({k: os.path.expanduser(v) for k, v in c.items() if k == "filename" or k == "keyfile"})
        log.error(f"Opening DB: {c['filename']}")
        from pykeepass import PyKeePass
        self.kdbx = PyKeePass(**c)

    def get(self, **kwargs) -> Iterator[str]:
        '''

        :param kwargs:
        :return: decoded password entry
        '''
        r = self.kdbx.find_entries(**kwargs)
        if r is None:
            return iter(())
        elif isinstance(r, list):
            return map(lambda e: e.password, iter(r))
        else:
            # attachment?
            return map(lambda e: e.password, iter([r]))

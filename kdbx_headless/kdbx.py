from __future__ import annotations

import logging
import os
import threading
import time
from typing import Iterator, Dict

import secretstorage

log = logging.getLogger(__name__)


class KDBXService:
    Threshold = 15.0  # seconds

    def __init__(self):
        self._cleanup_task = threading.Timer(KDBXService.Threshold, self._close)
        self._last_access = time.time()

    def get(self, **kwargs) -> Iterator[str]:
        pass

    def _reschedule(self):
        try:
            self._cleanup_task.cancel()
            self._cleanup_task = threading.Timer(KDBXService.Threshold, self._close)
            self._cleanup_task.start()
            log.debug("Rescheduled connection cleanup")
        except Exception as e:
            log.exception("Cannot reschedule cleanup")
            self._cleanup_task = threading.Timer(KDBXService.Threshold, self._close)
            self._cleanup_task.start()

    def _open(self):
        pass

    def _close(self):
        pass


class KDBXProxy(KDBXService):
    """
    Use when the KDBX should be opened not by kdbx-headless process
    """

    def __init__(self, kdbx: Dict[str, str]):
        super().__init__()
        self.db_name = kdbx['db_name']
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
            if (time.time() - self._last_access) >= KDBXService.Threshold:
                self.connection.close()
                log.info("Closed DBUS connection")


class KDBX(KDBXService):
    def __init__(self, kdbx: Dict[str, str]) -> KDBX:
        super().__init__()
        c = kdbx.copy()
        c.update({k: os.path.expanduser(v) for k, v in c.items() if k == "filename" or k == "keyfile"})
        self.kdbx_config = c
        self._kdbx_lock = threading.RLock()
        log.error(f"Opening DB: {self.kdbx_config['filename']}")
        self._open()

    def get(self, **kwargs) -> Iterator[str]:
        '''

        :param kwargs:
        :return: decoded password entry
        '''
        with self._kdbx_lock:
            self._open()
            self._reschedule()
            r = self.kdbx.find_entries(**kwargs)
            if r is None:
                return iter(())
            elif isinstance(r, list):
                return map(lambda e: e.password, iter(r))
            else:
                # attachment?
                return map(lambda e: e.password, iter([r]))

    def _open(self):
        with self._kdbx_lock:
            from pykeepass import PyKeePass
            self.kdbx = PyKeePass(**self.kdbx_config)
            self._last_access = time.time()

    def _close(self):
        log.info("Closing KDBX DB")
        with self._kdbx_lock:
            if (time.time() - self._last_access) >= KDBXService.Threshold:
                self.kdbx = None  # how to properly close PyKeePass?
                log.info("Closed KDBX DB")

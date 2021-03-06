from __future__ import annotations

import logging
import os
import threading
import time
import base64
from typing import Iterator, Dict, Union, List

import secretstorage
from pykeepass.entry import Entry

from kdbx_headless.spec import Secret

log = logging.getLogger(__name__)


class KDBXService:
    Threshold = 15.0  # seconds

    def __init__(self):
        self._cleanup_task = threading.Timer(KDBXService.Threshold, self._close)
        self._last_access = time.time()

    def get(self, **kwargs) -> Iterator[Secret]:
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

    def __init__(self, db_name: str) -> KDBXProxy:
        super().__init__()
        self.db_name = db_name
        self._dbus_lock = threading.RLock()

    def get(self, **kwargs) -> Iterator[Secret]:
        with self._dbus_lock:
            connection = self._open()
            self._reschedule()
            try:
                # we could fetch it all and close right here
                # todo how to handle KDBX attachments? - might be impossible and this is a problem since there is a limit for password length in keepassxc
                secret_service = next(
                    filter(
                        lambda c: c.collection_path == f"/org/freedesktop/secrets/collection/{self.db_name}",
                        secretstorage.get_all_collections(connection)
                    )
                )
                return map(
                    lambda i: Secret(i.get_secret().decode("utf-8")),
                    secret_service.search_items({**kwargs})
                )
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
    def __init__(self, filename: str, password: str = None, keyfile: str = None) -> KDBX:
        super().__init__()
        self.filename = os.path.expanduser(filename)
        if keyfile is not None:
            self.keyfile = os.path.expanduser(keyfile)
        else:
            self.keyfile = None
        self.password = password
        self._kdbx_lock = threading.RLock()

    def get(self, **kwargs) -> Iterator[Secret]:
        '''

        :param kwargs:
        :return: decoded password entry
        '''

        def with_attachments(it: Iterator[Entry]) -> Iterator[Secret]:
            def parse_entry(e: Entry) -> Secret:
                password = e.password
                attachments = []
                for at in e.attachments:
                    try:
                        attachments.append((at.filename, at.data.decode("utf-8")))
                    except UnicodeDecodeError as e:
                        log.error(f"Cannot decode: {at.filename} as UTF-8, performing base64")
                        attachments.append((at.filename, base64.b64encode(at.data)))
                return Secret(password, attachments)

            return map(lambda e: parse_entry(e), it)

        def adjust_path(key: str, value: str) -> Union[List[str], str]:
            if key == "path" and not isinstance(value, list):
                return [value]
            else:
                return value

        with self._kdbx_lock:
            self._open()
            self._reschedule()
            k = {k: adjust_path(k, v) for k, v in kwargs.items()}
            log.debug(f"KDBX query: {k}")
            r = self.kdbx.find_entries(**k)
            if r is None:
                log.info("No results")
                return iter(())
            elif isinstance(r, list):
                return with_attachments(iter(r))
            else:
                return with_attachments(iter([r]))

    def _open(self):
        with self._kdbx_lock:
            from pykeepass import PyKeePass
            self.kdbx = PyKeePass(filename=self.filename, password=self.password, keyfile=self.keyfile)
            self._last_access = time.time()

    def _close(self):
        log.info("Closing KDBX DB")
        with self._kdbx_lock:
            if (time.time() - self._last_access) >= KDBXService.Threshold:
                self.kdbx = None  # how to properly close PyKeePass?
                log.info("Closed KDBX DB")

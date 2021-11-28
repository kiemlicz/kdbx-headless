from __future__ import annotations

import logging
import os
import threading
from typing import Iterator, Dict

import secretstorage

log = logging.getLogger(__name__)


class KDBXService:
    def get(self, **kwargs) -> Iterator[str]:
        pass

    def close(self) -> None:
        pass


class KDBXProxy(KDBXService):
    """
    Use when the KDBX should be opened not by kdbx-headless process
    """

    def __init__(self, kdbx: Dict[str, str]):
        self.db_name = kdbx['db_name']
        self._dbus_lock = threading.RLock()

    def get(self, **kwargs) -> Iterator[str]:
        # with self._dbus_lock:  # since iterator is returned and consumption is outside this method don't lock here
        connection = self._open()
        try:
            secret_service = next(filter(
                lambda c: c.collection_path == f"/org/freedesktop/secrets/collection/{self.db_name}",
                secretstorage.get_all_collections(connection)
            ))
            return map(lambda i: i.get_secret().decode("utf-8"), secret_service.search_items({**kwargs}))
        except StopIteration as e:
            msg = f"Cannot find DB: {self.db_name}"
            log.exception(msg)
            raise RuntimeError(msg) from e

    def _open(self):
        log.info("Opening DBUS connection")
        with self._dbus_lock:
            self.connection = secretstorage.dbus_init()
            return self.connection

    def close(self):
        log.info("Closing DBUS connection")
        with self._dbus_lock:
            self.connection.close()


class KDBX(KDBXService):
    def __init__(self, kdbx: Dict[str, str]) -> KDBX:
        c = kdbx.copy()
        c.update({k: os.path.expanduser(v) for k, v in c.items() if k == "file" or k == "keyfile"})
        file = c.pop('file')  # fixme don't do this
        log.error(f"Opening DB: {file}")
        from pykeepass import PyKeePass
        self.kdbx = PyKeePass(file, **c)

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

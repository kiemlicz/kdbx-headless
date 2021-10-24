from __future__ import annotations
import logging
from contextlib import closing
from typing import Generator, Iterator

import secretstorage
from jeepney.io.blocking import DBusConnection
from secretstorage import Item

from kdbx_headless import app
from flask import session
log = logging.getLogger(__name__)


# def start():
#     # kdbx = KDBX(secretstorage.dbus_init(), app.config.get("DB_NAME"))
#     with closing(secretstorage.dbus_init()) as conn:
#         kdbx = KDBX(conn, app.config.get("DB_NAME"))
#         session['kdbx'] = kdbx

class KDBXService:
    def get(self, **kwargs) -> Iterator[Item]:
        pass


class KDBXProxy(KDBXService):
    def __init__(self, connection: DBusConnection, db_name: str):
        try:
            self.secret_service = next(filter(
                lambda c: c.collection_path == f"/org/freedesktop/secrets/collection/{db_name}",
                secretstorage.get_all_collections(connection)
            ))
        except StopIteration as e:
            msg = f"Cannot find DB: {db_name}"
            log.exception(msg)
            raise RuntimeError(msg) from e

    def get(self, **kwargs) -> Iterator[Item]:
        return self.secret_service.search_items({**kwargs})


class KDBX(KDBXService):
    def __init__(self, db_file: str, db_passwod: str, db_keyfile: str):
        from pykeepass import PyKeePass
        self.kdbx = PyKeePass(db_file, db_passwod, db_keyfile)

    def get(self, **kwargs) -> Iterator[Item]:
        return self.kdbx.find_entries(**kwargs)

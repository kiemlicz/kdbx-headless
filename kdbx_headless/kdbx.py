import logging
from contextlib import closing

import secretstorage
from jeepney.io.blocking import DBusConnection

from kdbx_headless import app
from flask import g
log = logging.getLogger(__name__)


def start():
    # kdbx = KDBX(secretstorage.dbus_init(), app.config.get("DB_NAME"))
    with closing(secretstorage.dbus_init()) as conn, app.app_context() as a:
        kdbx = KDBX(conn, app.config.get("DB_NAME"))
        a.g["KDBX"] = kdbx


class KDBX:
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

    def get(self, key: str, value: str):  ## types
        return self.secret_service.search_items({key: value})

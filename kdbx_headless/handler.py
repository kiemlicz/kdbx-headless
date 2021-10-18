import logging
from contextlib import closing

import secretstorage

from kdbx_headless import app
from flask import g
log = logging.getLogger(__name__)

# with closing(secretstorage.dbus_init()) as conn:
#     from . import kdbx
#
#     kdbx = kdbx.KDBX(conn, app.config.get("DB_NAME"))

@app.route('/bla')
def bla():
    return "bla"


@app.route('/secret/<name>/<val>', methods=['GET'])
def secret(name, val):
    kdbx = g["KDBX"]
    res = kdbx.get(name, val)

    return list(res)

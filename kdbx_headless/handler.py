import logging
from contextlib import closing

import secretstorage

from kdbx_headless import app
from kdbx_headless.kdbx import KDBX
from flask import g
log = logging.getLogger(__name__)

# with closing(secretstorage.dbus_init()) as conn:
#     from . import kdbx
#
#     kdbx = kdbx.KDBX(conn, app.config.get("DB_NAME"))

@app.route('/bla')
def bla():
    return "bla"


# session is kept in cookie - bad place, really bad!! but check it
# since the DB is open we can open/close the dbus conn every time
def get_kdbx():
    if 'kdbx' not in g:
        log.info("KDBX not found in current context, opening")
        # with closing(secretstorage.dbus_init()) as conn:
        #     kdbx = KDBX(conn, app.config.get("DB_NAME"))
        #     g.kdbx = kdbx

        g.kdbx = KDBX(secretstorage.dbus_init(), app.config.get("DB_NAME"))  # fixme fix closing the dbusconnection
    return g.kdbx


@app.route('/secret/<name>/<val>', methods=['GET'])
def secret(name, val):
    kdbx = get_kdbx()
    res = kdbx.get(name, val)
    return list(res)

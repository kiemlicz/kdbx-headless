import json
import logging
from contextlib import closing
from itertools import islice
import secretstorage

from kdbx_headless import app
from kdbx_headless.kdbx import KDBXProxy, KDBXService
from flask import g, request
log = logging.getLogger(__name__)

# with closing(secretstorage.dbus_init()) as conn:
#     from . import kdbx
#
#     kdbx = kdbx.KDBX(conn, app.config.get("DB_NAME"))


@app.route('/health')
def bla():
    return "OK"


# session is kept in cookie - bad place, really bad!! but check it
# since the DB is open we can open/close the dbus conn every time
def get_kdbx() -> KDBXService:
    # read from config which type to use: proxy or DB
    if 'kdbx' not in g:
        log.info("KDBX not found in current context, opening")
        # with closing(secretstorage.dbus_init()) as conn:
        #     kdbx = KDBX(conn, app.config.get("DB_NAME"))
        #     g.kdbx = kdbx

        g.kdbx = KDBXProxy(secretstorage.dbus_init(), app.config.get("DB_NAME"))  # fixme fix closing the dbusconnection
    return g.kdbx


@app.route('/secret/<name>/<val>', methods=['GET'])
def secret(name, val):
    max_items = request.args.get("max_items", 1, int)  # fixme const
    kwargs = {name: val}
    kwargs.update(request.args)  # check if there are some additional arguments
    kwargs.pop("max_items")
    kdbx = get_kdbx()
    log.info(f"Finding max: {max_items} for {kwargs}")
    items = list(islice(map(lambda i: i.get_secret().decode("utf-8"), kdbx.get(**kwargs)), max_items))
    j = {"secrets": items}
    return json.dumps(j)

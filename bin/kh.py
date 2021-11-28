#!/usr/bin/env python3

import argparse
import logging
import os
import urllib.parse

from kdbx_headless.application import create_app


log = logging.getLogger()

parser = argparse.ArgumentParser(description='Run KDBX simple REST API server')
parser.add_argument('--ssl', help="cert dir (must contain: kdbx-headless.crt, kdbx-headless.key)", required=True)
parser.add_argument('--bind', help="bind address (host:port)", required=False, default="127.0.0.1:5000")
args = parser.parse_args()

r = urllib.parse.urlsplit(args.bind)
context = (os.path.join(args.ssl, "kdbx-headless.crt"), os.path.join(args.ssl, "kdbx-headless.key"))
app = create_app()
# todo setup mtls
app.run(host=r.hostname, port=r.port, ssl_context=context)

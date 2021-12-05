#!/usr/bin/env python3

import argparse
import logging
import os
import ssl

from kdbx_headless.application import create_app

log = logging.getLogger()

parser = argparse.ArgumentParser(description='Run KDBX simple REST API server')
parser.add_argument('--ssl', help="cert dir (must contain: kdbx-headless.crt, kdbx-headless.key)", required=True)
parser.add_argument('--bind', help="bind ip address", required=False, default="127.0.0.1")
parser.add_argument('--port', help="bind port", required=False, default="5000")
args = parser.parse_args()

app_cert = os.path.join(args.ssl, "kdbx-headless.crt")
app_key = os.path.join(args.ssl, "kdbx-headless.key")
ca_cert = os.path.join(args.ssl, "ca.crt")
ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile=ca_cert)
ssl_context.load_cert_chain(certfile=app_cert, keyfile=app_key)
ssl_context.verify_mode = ssl.CERT_REQUIRED  # cert required causes mtls, ssl.CERT_OPTIONAL for debug
app = create_app()
app.run(host=args.bind, port=args.port, ssl_context=ssl_context)

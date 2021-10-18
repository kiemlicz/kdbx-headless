#!/usr/bin/env python3

import argparse
import logging
import os

from kdbx_headless import app

parser = argparse.ArgumentParser(description='Run KDBX simple REST API server')
parser.add_argument('--log', help="log level (TRACE, DEBUG, INFO, WARN, ERROR)", required=False, default="INFO")
parser.add_argument('--ssl', help="cert dir (must contain: kdbx-headless.crt, kdbx-headless.key)", required=False)
parser.add_argument('--config', help="config file", required=False, default="/etc/default/kdbx-headless.json")
args = parser.parse_args()

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)-8s] %(message)s',
    level=logging.getLevelName(args.log),
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger()

config = args.config
if not os.path.isabs(config):
    config = os.path.abspath(config)

app.config.from_json(config)

if args.ssl:
    context = (os.path.join(ssl, "kdbx-headless.crt"), os.path.join(ssl, "kdbx-headless.key"))
    app.run(host="0.0.0.0", ssl_context=context)
else:
    app.run(host="0.0.0.0")

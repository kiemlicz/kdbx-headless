import json
import logging
import os
import yaml

from flask import Flask, request, Response
from deepmerge import always_merger
from itertools import islice
from kdbx_headless.kdbx_provider import SecretProvider

from kdbx_headless.utils import _multi_dict_to_dict

files = [
    "kdbx-cfg.yaml",
    "/etc/kdbx-headless/kdbx-cfg.yaml",
    ".local/kdbx-cfg.yaml"
]  # starts with the default, the last is the most 'specific'

config = {}
for file in filter(lambda f: os.path.exists(f), files):
    with open(file) as f:
        d = yaml.safe_load(f)
        always_merger.merge(config, d)

log_config = config['log']
log_level = log_config['level']
logging.basicConfig(
    format=log_config['pattern'],
    level=logging.getLevelName(log_level),
    datefmt=log_config['timestamp']
)
log = logging.getLogger(__name__)

provider = SecretProvider(config)

app = Flask(__name__)
app.logger.setLevel(log_level)
if 'flask' in config:
    app.config.from_mapping(config['flask'])


@app.route("/secret", methods=['GET'])
def secret():
    kdbx = provider.service
    d = _multi_dict_to_dict(request.args)
    max_items = int(d.get("max_items", 1))
    log.info(f"Query: {d}, limit: {max_items}")
    j = json.dumps(
        {
            "secrets": list(islice(kdbx.get(**d), max_items))
        }
    )
    return Response(j, mimetype='application/json')


@app.route("/health", methods=['GET'])
def health():
    return "OK"

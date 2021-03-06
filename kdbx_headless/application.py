import logging
import os
import yaml
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from flask import Flask, request
from deepmerge import always_merger

from flask_apispec import marshal_with, FlaskApiSpec, doc, use_kwargs
from marshmallow import fields

from kdbx_headless.kdbx_provider import SecretProvider

from kdbx_headless.spec import SecretSchema, Secret

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

SELECTOR_KEY = config['selector_key']

log_config = config['log']
log_level = log_config['level']
logging.basicConfig(
    format=log_config['pattern'],
    level=logging.getLevelName(log_level),
    datefmt=log_config['timestamp']
)
log = logging.getLogger(__name__)

try:
    provider = SecretProvider(config)
except Exception as e:
    msg = f"Cannot instantiate secret provider, configured class: {config['kdbx_class']}"
    log.exception(msg)
    raise RuntimeError(msg) from e

app = Flask(__name__)
app.logger.setLevel(log_level)
if 'flask' in config:
    app.config.from_mapping(config['flask'])

app.config.update(
    {
        'APISPEC_SPEC': APISpec(
            title="KDBX headless",
            version="0.1",
            openapi_version="3.0.2",
            plugins=[MarshmallowPlugin()],
        ),
        'APISPEC_SWAGGER_URL': '/swagger/',
    }
)
docs = FlaskApiSpec(app)

@app.route("/secret", methods=['GET'])
@marshal_with(SecretSchema(many=True))
@use_kwargs(
    {
        'creds': fields.Str(required=False, metadata={'description': "Key to search Secret Service"}),
        'path': fields.List(fields.Str(), required=False, metadata={'description': "Path within KDBX database"})
    },
    location='query'
)
@doc(description="Fetch secret entry")
def secret(**kwargs):
    kdbx = provider.service
    log.info(f"Query: {kwargs}")
    return list(kdbx.get(**kwargs))


@app.route("/health", methods=['GET'])
def health():
    return "OK"


docs.register(secret)

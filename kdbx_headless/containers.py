import logging
import os.path

import yaml
from deepmerge import always_merger
from dependency_injector import containers, providers

from . import kdbx

log = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[".handler"])
    files = [
        "kdbx-cfg.yaml",
        "/etc/kdbx-headless/kdbx-cfg.yaml",
        ".local/kdbx-cfg.yaml"
    ]  # starts with the default, the last is the most 'specific'
    config = {}
    for file in filter(lambda f: os.path.exists(f), files):
        with open(file) as f:
            log.debug(f"Loading file: {file}")
            d = yaml.safe_load(f)
            always_merger.merge(config, d)

    container_config = providers.Configuration()
    container_config.from_dict(config)
    klass = getattr(kdbx, config['kdbx_class'])  # can't access container_config here
    kdbx = providers.Singleton(
        klass,
        container_config.kdbx
    )

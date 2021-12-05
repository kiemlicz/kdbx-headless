import logging

from flask import Flask

from .containers import Container
from . import handler


def create_app() -> Flask:
    container = Container()
    app = Flask(__name__)
    app.container = container
    cfg = container.container_config
    log_config = cfg.log
    log_level = log_config.level.as_(str)()
    logging.basicConfig(
        format=log_config.pattern.as_(str)(),
        level=logging.getLevelName(log_level),
        datefmt=log_config.timestamp.as_(str)()
    )
    app.logger.setLevel(log_level)
    app.add_url_rule("/health", "health", handler.health, methods=['GET'])
    app.add_url_rule("/secret", "secret", handler.secret, methods=['GET'])
    return app
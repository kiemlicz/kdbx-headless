import json
import logging
from itertools import islice
from typing import Dict, Any

from dependency_injector.wiring import inject, Provide
from flask import request, Response

from .containers import Container
from .kdbx import KDBXService

log = logging.getLogger(__name__)


def health():
    return "OK"


@inject
def secret(kdbx: KDBXService = Provide[Container.kdbx]):
    d = _multi_dict_to_dict(request.args)
    max_items = int(d.get("max_items", 1))
    log.info(f"Query: {d}, limit: {max_items}")
    j = json.dumps({
        "secrets": list(islice(kdbx.get(**d), max_items))
    })
    return Response(j, mimetype='application/json')


def _multi_dict_to_dict(md) -> Dict[str, Any]:
    d = {}
    for k, v in md.items(multi=True):
        if k in d and isinstance(d[k], list):
            d[k].append(v)
        elif k in d:
            prev = d.pop(k)
            d[k] = [prev, v]
        else:
            d[k] = v
    return d

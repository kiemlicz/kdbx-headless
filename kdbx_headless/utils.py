from typing import Dict, Any


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

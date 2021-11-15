from typing import Any, Dict
from django.db.models.constants import LOOKUP_SEP

EQUALS_LOOKUP = "exact"
LOOKUPS = {
    EQUALS_LOOKUP,
    "ne",
    "isnull",
    "gte",
    "gt",
    "lte",
    "lt",
}


def iterate_over_nested_dict(data, names=None):
    names = names or []
    for k, v in data.items():
        names.append(k)
        if isinstance(v, dict):
            yield from iterate_over_nested_dict(v, names)
        else:
            yield LOOKUP_SEP.join(names), v
        names.pop()


def restore_filter(filters):
    return {k: v for k, v in iterate_over_nested_dict(filters)}


def build_filter(filters: Dict[str, Any], kwargs: Dict[str, Any]):
    for k, v in kwargs.items():
        node = filters
        names = k.split(LOOKUP_SEP)
        lookup = names[-1]
        for name in names[:-1]:
            if name not in node:
                node[name] = {}
            node = node[name]
        if lookup not in LOOKUPS:
            node[lookup] = {EQUALS_LOOKUP: v}
        else:
            node[lookup] = v
    return filters

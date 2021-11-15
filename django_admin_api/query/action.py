from dataclasses import asdict

import requests

from .base import BaseApiQuerySet, Actions
from ..filters import build_filter


class ActionsApiQuerySet(BaseApiQuerySet):
    def request(self, action: Actions):
        data = {k: v for k, v in asdict(self.query).items() if v}
        if "filters" in data:
            data["filters"] = build_filter(data["filters"])
        r = requests.post(self._get_url(action), json={"action": action.value, **data})
        r.raise_for_status()
        return r.json()

    def extract(self, raw, action: Actions):
        if action == Actions.count:
            return raw["count"]
        if action == Actions.list:
            return [self.serializer.deserialize(obj) for obj in raw["data"]]
        return self.serializer.deserialize(raw["data"][0])

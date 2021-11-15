from typing import Dict, List, Union

import requests

from .base import BaseApiQuerySet, Actions


class RestApiQuerySet(BaseApiQuerySet):
    def request(self, action: Actions) -> Union[Dict, List]:
        url = self._get_url(action)
        if action == Actions.count:
            r = requests.get(url, params=self.query.filters)
        elif action == Actions.list:
            params = {**self.query.filters}
            if self.query.order_by:
                params["order_by"] = self.query.order_by
            r = requests.get(url, params=params)
        elif action == Actions.update:
            r = requests.patch(url, params=self.query.filters, json=self.query.update)
        elif action == Actions.create:
            r = requests.post(url, json=self.query.data)
        elif action == Actions.delete:
            r = requests.delete(url, params=self.query.filters)
        r.raise_for_status()
        return r.json()

    def extract(self, raw, action: Actions):
        if action == Actions.count:
            return raw["count"]
        if action == Actions.list:
            return [self.serializer.deserialize(obj) for obj in raw["data"]]
        return self.serializer.deserialize(raw["data"][0])

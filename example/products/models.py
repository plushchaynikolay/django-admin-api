from django.db import models
from django_admin_api.query import (
    AbstractSerializer,
    RestApiQuerySet,
    ActionsApiQuerySet,
)
from django_admin_api.models import ApiModel


class Product(models.Model):
    name = models.CharField(max_length=255)

    def as_dict(self):
        return {"id": self.pk, "name": self.name}


class ActionApiProductSerializer(AbstractSerializer[Product]):
    def serialize(self, model: "ActionApiProduct"):
        return {"id": model.id, "name": model.name}

    def deserialize(self, raw) -> "ActionApiProduct":
        return ActionApiProduct(id=raw.get("id"), name=raw.get("name"))


class ActionApiProduct(ApiModel):
    _url = "http://127.0.0.1:8000/products/action/"
    _serializer = ActionApiProductSerializer()

    name = models.CharField(max_length=255)

    objects = ActionsApiQuerySet.as_manager()()


class RestApiProductSerializer(AbstractSerializer[Product]):
    def serialize(self, model: "RestApiProduct"):
        return {"id": model.id, "name": model.name}

    def deserialize(self, raw) -> "ActionApiProduct":
        return RestApiProduct(id=raw.get("id"), name=raw.get("name"))


class RestApiProduct(ApiModel):
    _url = "http://127.0.0.1:8000/products/rest/"
    _count_url = "http://127.0.0.1:8000/products/rest/count/"
    _serializer = RestApiProductSerializer()

    name = models.CharField(max_length=255)

    objects = RestApiQuerySet.as_manager()()

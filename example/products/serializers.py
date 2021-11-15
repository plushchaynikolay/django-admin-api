from typing import Any, Dict
from django_admin_api.query import AbstractSerializer

from products.models import Product


class ProductSerializer(AbstractSerializer[Product]):
    def serialize(self, model: Product) -> Dict[str, Any]:
        return {"id": model.id, "name": model.name}

    def deserialize(self, raw: Dict[str, Any]) -> Product:
        return Product(id=raw.get("id"), name=raw.get("name"))

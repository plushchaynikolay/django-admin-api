import json
from django.http import HttpRequest, HttpResponse, JsonResponse

from django.views import View
from django_admin_api.filters import restore_filter

from products.models import Product
from products.serializers import ProductSerializer


class RestProductCountView(View):
    model = Product
    serializer = ProductSerializer()

    def get_queryset(self, request: HttpRequest):
        order_by = request.GET.getlist("order_by")
        filters = request.GET.dict()
        filters.pop("order_by", None)
        limit = filters.pop("limit", None)
        offset = filters.pop("offset", None)

        qs = self.model.objects.all()
        if filters:
            qs = qs.filter(**filters)
        if order_by:
            qs = qs.order_by(*order_by)
        if limit:
            offset = offset or 0
            qs = qs[offset : offset + limit]
        return qs

    def get(self, request: HttpRequest):
        qs = self.get_queryset(request)
        return JsonResponse(data={"count": qs.count()})


class RestProductsView(RestProductCountView):
    def get(self, request: HttpRequest):
        qs = self.get_queryset(request)
        return JsonResponse(data={"data": list(map(self.serializer.serialize, qs))})

    def post(self, request: HttpRequest):
        data = list(map(self.serializer.deserialize, json.loads(request.body)))
        data = self.model.objects.bulk_create(data)
        return JsonResponse(data={"data": list(map(self.serializer.serialize, data))})

    def patch(self, request: HttpRequest):
        qs = self.get_queryset(request)
        count = qs.update(**json.loads(request.body))
        return JsonResponse(data={"count": count})

    def delete(self, request: HttpRequest):
        count, _ = self.get_queryset(request).delete()
        return JsonResponse(data={"count": count})


class ActionProductsView(View):
    model = Product
    serializer = ProductSerializer()

    def get_queryset(
        self,
        filters: dict = None,
        excludes: dict = None,
        order_by: list = None,
        select_related: list = None,
        limit=None,
        offset=None,
        **kwargs
    ):
        qs = self.model.objects.all()
        if filters:
            qs = qs.filter(**restore_filter(filters))
        if excludes:
            qs = qs.exclude(**restore_filter(excludes))
        if order_by:
            qs = qs.order_by(*order_by)
        if select_related:
            qs = qs.select_related(*select_related)
        if limit:
            offset = offset or 0
            qs = qs[offset : offset + limit]
        return qs

    def post(self, request: HttpRequest) -> HttpResponse:
        request.json = json.loads(request.body)
        action = request.json.get("action", "list")
        return getattr(self, action)(request)

    def list(self, request: HttpRequest):
        qs = self.get_queryset(**request.json)
        return JsonResponse(data={"data": list(map(self.serializer.serialize, qs))})

    def count(self, request: HttpRequest):
        qs = self.get_queryset(**request.json)
        return JsonResponse(data={"count": qs.count()})

    def create(self, request: HttpRequest):
        data = list(map(self.serializer.deserialize, request.json["data"]))
        data = self.model.objects.bulk_create(data)
        return JsonResponse(data={"data": list(map(self.serializer.serialize, data))})

    def update(self, request: HttpRequest):
        qs = self.get_queryset(**request.json)
        count = qs.update(**request.json["update"])
        return JsonResponse(data={"count": count})

    def delete(self, request: HttpRequest):
        count, _ = self.get_queryset(**request.json).delete()
        return JsonResponse(data={"count": count})

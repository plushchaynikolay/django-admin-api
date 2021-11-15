from django.contrib import admin
from .models import ActionApiProduct, Product, RestApiProduct


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(ActionApiProduct)
class ActionApiProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(RestApiProduct)
class RestApiProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

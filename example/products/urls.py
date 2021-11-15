from django.urls import path
from .views import RestProductsView, ActionProductsView, RestProductCountView

app_name = "products"

urlpatterns = [
    path("action/", ActionProductsView.as_view()),
    path("rest/", RestProductsView.as_view()),
    path("rest/count/", RestProductCountView.as_view()),
]

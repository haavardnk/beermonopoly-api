from django.urls import include, path
from rest_framework.routers import DefaultRouter
from beers.api.views import (BeerViewSet)

router = DefaultRouter()
router.register(r"beers", BeerViewSet, basename="beers")

urlpatterns = [
    path("", include(router.urls)),
]
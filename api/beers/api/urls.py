from django.urls import include, path
from rest_framework.routers import DefaultRouter
from beers.api.views import BeerViewSet, StoreViewSet, StockViewSet

router = DefaultRouter()
router.register(r"beers", BeerViewSet, basename="beers")
router.register(r"stores", StoreViewSet, basename="stores")
router.register(r"stock", StockViewSet, basename="stock")

urlpatterns = [
    path("", include(router.urls)),
]
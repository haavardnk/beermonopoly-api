from django.urls import include, path
from rest_framework.routers import DefaultRouter
from beers.api.views import (
    BeerViewSet,
    StoreViewSet,
    StockViewSet,
    MatchViewSet,
    WrongMatchViewSet,
)

router = DefaultRouter()
router.register(r"beers", BeerViewSet, basename="beer")
router.register(r"stores", StoreViewSet, basename="store")
router.register(r"stock", StockViewSet, basename="stock")
router.register(r"match", MatchViewSet, basename="match")
router.register(r"wrongmatch", WrongMatchViewSet, basename="wrongmatch")

urlpatterns = [
    path("", include(router.urls)),
]

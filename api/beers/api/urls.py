from django.urls import include, path
from rest_framework.routers import DefaultRouter
from beers.api.views import BeerViewSet, StoreViewSet, StockViewSet, MatchViewSet

router = DefaultRouter()
router.register(r"beers", BeerViewSet, basename="beer")
router.register(r"stores", StoreViewSet, basename="store")
router.register(r"stock", StockViewSet, basename="stock")
router.register(r"match", MatchViewSet, basename="match")

urlpatterns = [
    path("", include(router.urls)),
]

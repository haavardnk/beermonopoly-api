from beers.api.views import UntappdLogin
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.conf import settings
from beers.api.views import (
    BeerViewSet,
    StoreViewSet,
    StockViewSet,
    MatchViewSet,
    WrongMatchViewSet,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register(r"beers", BeerViewSet, basename="beer")
router.register(r"stores", StoreViewSet, basename="store")
router.register(r"stock", StockViewSet, basename="stock")
router.register(r"match", MatchViewSet, basename="match")
router.register(r"wrongmatch", WrongMatchViewSet, basename="wrongmatch")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "auth/untappd/",
        UntappdLogin.as_view(),
        name="untappd_login",
    ),
    path("auth/", include("dj_rest_auth.urls")),
]

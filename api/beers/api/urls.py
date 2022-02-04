from beers.api.views import UntappdLogin
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.conf import settings
from beers.api.views import (
    BeerViewSet,
    StoreViewSet,
    StockViewSet,
    WrongMatchViewSet,
    ReleaseViewSet,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register(r"beers", BeerViewSet, basename="beer")
router.register(r"stores", StoreViewSet, basename="store")
router.register(r"stock", StockViewSet, basename="stock")
router.register(r"wrongmatch", WrongMatchViewSet, basename="wrongmatch")
router.register(r"release", ReleaseViewSet, basename="release")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "auth/untappd/",
        UntappdLogin.as_view(),
        name="untappd_login",
    ),
    path("auth/", include("dj_rest_auth.urls")),
]

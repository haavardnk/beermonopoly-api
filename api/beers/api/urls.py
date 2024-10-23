from django.urls import include, path
from django.urls import re_path
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.conf import settings
from beers.api.views import (
    BeerViewSet,
    StoreViewSet,
    StockViewSet,
    WrongMatchViewSet,
    ReleaseViewSet,
    StockChangeViewSet,
    add_wishlist,
    remove_wishlist,
    get_checked_in_styles,
    add_remove_tasted,
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
router.register(r"stockchange", StockChangeViewSet, basename="stockchange")

urlpatterns = [
    path("", include(router.urls)),
    re_path(r"^add_wishlist", add_wishlist, name="add_wishlist"),
    re_path(r"^remove_wishlist", remove_wishlist, name="remove_wishlist"),
    re_path(
        r"^auth/checked_in_styles", get_checked_in_styles, name="checked_in_styles"
    ),
    re_path(r"^beers/add_remove_tasted", add_remove_tasted, name="add_remove_tasted"),
]

from distutils.util import strtobool
from rest_framework import permissions, filters, renderers
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from beers.api.filters import NullsAlwaysLastOrderingFilter, BeerFilter
from beers.models import Beer, Stock, Store, WrongMatch
from beers.api.pagination import Pagination, LargeResultPagination
from beers.api.serializers import (
    BeerSerializer,
    AuthenticatedBeerSerializer,
    StockSerializer,
    StoreSerializer,
    WrongMatchSerializer,
)
from allauth.socialaccount.providers.untappd.views import UntappdOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView


class StaffBrowsableMixin(object):
    def get_renderers(self):
        """
        Add Browsable API renderer if user is staff.
        """
        rends = self.renderer_classes
        if self.request.user and self.request.user.is_staff:
            rends.append(renderers.BrowsableAPIRenderer)
        return [renderer() for renderer in rends]


class UntappdLogin(SocialLoginView):
    adapter_class = UntappdOAuth2Adapter


class BeerViewSet(StaffBrowsableMixin, ModelViewSet):
    pagination_class = Pagination
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    filter_backends = (
        filters.SearchFilter,
        NullsAlwaysLastOrderingFilter,
        DjangoFilterBackend,
    )
    search_fields = [
        "vmp_name",
        "brewery",
        "sub_category",
        "style",
        "vmp_id",
        "untpd_id",
    ]
    ordering_fields = [
        "vmp_name",
        "brewery",
        "rating",
        "price",
        "created_at",
        "abv",
        "price_per_volume",
        "checkin__rating",
    ]
    filterset_class = BeerFilter

    def get_queryset(self):
        queryset = Beer.objects.all()
        beers = self.request.query_params.get("beers", None)
        user_checkin = self.request.query_params.get("user_checkin", None)
        user_wishlisted = self.request.query_params.get("user_wishlisted", None)
        if beers is not None:
            beers = list(int(v) for v in beers.split(","))
            queryset = queryset.filter(vmp_id__in=beers)
        if (
            user_checkin != None
            and strtobool(user_checkin) == True
            and self.request.user
            and self.request.user.is_authenticated
        ):
            queryset = queryset.filter(checkin__user=self.request.user)
        elif (
            user_checkin != None
            and strtobool(user_checkin) == False
            and self.request.user
            and self.request.user.is_authenticated
        ):
            queryset = queryset.exclude(checkin__user=self.request.user)
        if (
            user_wishlisted != None
            and strtobool(user_wishlisted) == True
            and self.request.user
            and self.request.user.is_authenticated
        ):
            queryset = queryset.filter(wishlist__user=self.request.user)
        elif (
            user_wishlisted != None
            and strtobool(user_wishlisted) == False
            and self.request.user
            and self.request.user.is_authenticated
        ):
            queryset = queryset.exclude(wishlist__user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_authenticated:
            return AuthenticatedBeerSerializer
        else:
            return BeerSerializer


class StoreViewSet(StaffBrowsableMixin, ModelViewSet):
    queryset = Store.objects.all().order_by("name")
    serializer_class = StoreSerializer
    pagination_class = LargeResultPagination
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ["name", "address", "store_id"]
    ordering_fields = ["name", "store_id"]
    ordering = ["name"]


class StockViewSet(StaffBrowsableMixin, ModelViewSet):
    queryset = Stock.objects.all().order_by("store__store_id")
    serializer_class = StockSerializer
    pagination_class = Pagination
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["store", "beer"]


class WrongMatchViewSet(StaffBrowsableMixin, ModelViewSet):
    queryset = WrongMatch.objects.all()
    serializer_class = WrongMatchSerializer
    pagination_class = Pagination
    permission_classes = [permissions.AllowAny]

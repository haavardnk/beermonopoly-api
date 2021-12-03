from rest_framework import permissions, filters, renderers
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from beers.models import Beer, Stock, Store, WrongMatch, ExternalAPI
from beers.api.pagination import Pagination
from beers.api.serializers import (
    BeerSerializer,
    AuthenticatedBeerSerializer,
    StockSerializer,
    StoreSerializer,
    WrongMatchSerializer,
    ChromeAuthSerializer,
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
        filters.OrderingFilter,
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
    ordering_fields = ["vmp_name", "brewery", "sub_category", "rating"]
    filterset_fields = ["style", "brewery"]

    def get_queryset(self):
        queryset = Beer.objects.all()
        beers = self.request.query_params.get("beers", None)
        if beers is not None:
            beers = list(int(v) for v in beers.split(","))
            queryset = queryset.filter(vmp_id__in=beers)

        return queryset

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_authenticated:
            return AuthenticatedBeerSerializer
        else:
            return BeerSerializer


class StoreViewSet(StaffBrowsableMixin, ModelViewSet):
    queryset = Store.objects.all().order_by("name")
    serializer_class = StoreSerializer
    pagination_class = Pagination
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


class ChromeAuthViewSet(StaffBrowsableMixin, ReadOnlyModelViewSet):
    queryset = ExternalAPI.objects.filter(name="untappd")
    serializer_class = ChromeAuthSerializer
    permission_classes = [permissions.AllowAny]

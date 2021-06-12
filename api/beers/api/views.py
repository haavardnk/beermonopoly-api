from rest_framework import generics, permissions, filters
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from beers.models import Beer, Stock, Store
from beers.api.pagination import Pagination
from beers.api.serializers import (
    BeerSerializer,
    StockSerializer,
    StoreSerializer,
    MatchSerializer,
)


class BeerViewSet(ModelViewSet):
    serializer_class = BeerSerializer
    pagination_class = Pagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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
        queryset = Beer.objects.filter(active=True)
        beers = self.request.query_params.get("beers", None)
        if beers is not None:
            beers = list(int(v) for v in beers.split(","))
            queryset = queryset.filter(vmp_id__in=beers)

        return queryset


class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all().order_by("name")
    serializer_class = StoreSerializer
    pagination_class = Pagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ["name", "address", "store_id"]
    ordering_fields = ["name", "store_id"]
    ordering = ["name"]


class StockViewSet(ModelViewSet):
    queryset = Stock.objects.all().order_by("store__store_id")
    serializer_class = StockSerializer
    pagination_class = Pagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["store", "beer"]


class MatchViewSet(ModelViewSet):
    queryset = Beer.objects.filter(match_manually=True)
    serializer_class = MatchSerializer
    pagination_class = Pagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

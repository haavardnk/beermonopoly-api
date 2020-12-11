from rest_framework import generics
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from beers.models import Beer, Stock, Store
from beers.api.pagination import Pagination
from beers.api.serializers import BeerSerializer, StockSerializer, StoreSerializer

class BeerViewSet(ModelViewSet):
    queryset = Beer.objects.filter(active=True).order_by("vmp_id")
    serializer_class = BeerSerializer
    pagination_class = Pagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Beer.objects.all().order_by("vmp_id")
        vmp_id = self.request.query_params.get("id", None)
        if vmp_id is not None:
            vmp_id = list(int(v) for v in vmp_id.split(','))
            queryset = queryset.filter(vmp_id__in=vmp_id, active=True)

        search = self.request.query_params.get("search", None)
        if search is not None:
            search = list(v for v in search.split(','))
            queryset = queryset.filter(vmp_name__search=search, active=True)

        return queryset

class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all().order_by("name")
    serializer_class = StoreSerializer
    pagination_class = Pagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class StockViewSet(ModelViewSet):
    queryset = Stock.objects.all().order_by("store__storeid")
    serializer_class = StockSerializer
    pagination_class = Pagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Stock.objects.all().order_by("store__storeid")
        storeid = self.request.query_params.get("store", None)
        if storeid is not None:
            storeid = storeid
            queryset = queryset.filter(store=storeid)

        beerid = self.request.query_params.get("beer", None)
        if beerid is not None:
            beerid = beerid
            queryset = queryset.filter(beer=beerid)


        return queryset

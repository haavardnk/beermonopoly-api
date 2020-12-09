from rest_framework import generics
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from beers.models import Beer
from beers.api.pagination import SmallSetPagination
from beers.api.serializers import BeerSerializer

class BeerViewSet(ModelViewSet):
    queryset = Beer.objects.all().order_by("beerid")
    serializer_class = BeerSerializer
    pagination_class = SmallSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Beer.objects.all().order_by("beerid")
        beerid = self.request.query_params.get("beerid", None)
        if beerid is not None:
            beerid = list(int(v) for v in beerid.split(','))
            queryset = queryset.filter(beerid__in=beerid)

        search = self.request.query_params.get("search", None)
        if search is not None:
            search = list(v for v in search.split(','))
            queryset = queryset.filter(name__search=search)

        return queryset
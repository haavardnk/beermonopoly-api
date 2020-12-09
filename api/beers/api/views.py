from rest_framework import generics
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from beers.models import Beer
from beers.api.pagination import SmallSetPagination
from beers.api.serializers import BeerSerializer

class BeerViewSet(ModelViewSet):
    queryset = Beer.objects.all().order_by("vmp_id")
    serializer_class = BeerSerializer
    pagination_class = SmallSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Beer.objects.all().order_by("vmp_id")
        vmp_id = self.request.query_params.get("vmp_id", None)
        if vmp_id is not None:
            vmp_id = list(int(v) for v in vmp_id.split(','))
            queryset = queryset.filter(vmp_id__in=vmp_id)

        search = self.request.query_params.get("search", None)
        if search is not None:
            search = list(v for v in search.split(','))
            queryset = queryset.filter(vmp_name__search=search)

        return queryset
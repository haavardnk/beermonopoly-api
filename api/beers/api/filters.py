from rest_framework import filters
from django.db.models import F
from django_filters import rest_framework as flt
from beers.models import Beer
from django.db.models import Q


class NullsAlwaysLastOrderingFilter(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            f_ordering = []
            for o in ordering:
                if not o:
                    continue
                if o[0] == "-":
                    f_ordering.append(F(o[1:]).desc(nulls_last=True))
                else:
                    f_ordering.append(F(o).asc(nulls_last=True))

            return queryset.order_by(*f_ordering)

        return queryset


class BeerFilter(flt.FilterSet):
    style = flt.CharFilter(method="custom_style_filter")
    store = flt.NumberFilter(field_name="stock__store", lookup_expr="exact")

    def custom_style_filter(self, queryset, name, value):
        query = Q()
        for val in value.split(","):
            query |= Q(style__icontains=val)
        return queryset.filter(query)

    class Meta:
        model = Beer
        fields = ["style", "brewery", "active", "store"]

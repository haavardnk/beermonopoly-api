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
    product_selection = flt.CharFilter(method="custom_product_selection_filter")
    store = flt.CharFilter(method="custom_store_filter")
    price_high = flt.NumberFilter(field_name="price", lookup_expr="lte")
    price_low = flt.NumberFilter(field_name="price", lookup_expr="gte")
    release = flt.CharFilter(method="custom_release_filter")

    def custom_style_filter(self, queryset, name, value):
        query = Q()
        for val in value.split(","):
            query |= Q(style__icontains=val)
        return queryset.filter(query).distinct()

    def custom_product_selection_filter(self, queryset, name, value):
        query = Q()
        for val in value.split(","):
            query |= Q(product_selection__iexact=val)
        return queryset.filter(query).distinct()

    def custom_store_filter(self, queryset, name, value):
        query = Q()
        for val in value.split(","):
            query |= Q(stock__store__exact=int(val))
        return queryset.filter(query).distinct()

    def custom_release_filter(self, queryset, name, value):
        query = Q()
        for val in value.split(","):
            query |= Q(release__name__iexact=val)
        return queryset.filter(query).distinct()

    class Meta:
        model = Beer
        fields = [
            "style",
            "brewery",
            "product_selection",
            "active",
            "store",
            "price_high",
            "price_low",
            "release",
        ]

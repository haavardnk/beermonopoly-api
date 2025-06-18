from django.db.models import F, Q, Count
from django.db.models.functions import Greatest
from django.contrib.postgres.aggregates import ArrayAgg
from rest_framework import permissions, filters, renderers
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from beers.api.filters import (
    NullsAlwaysLastOrderingFilter,
    BeerFilter,
    StockChangeFilter,
)
from beers.models import (
    Beer,
    Stock,
    Store,
    WrongMatch,
    Release,
    Wishlist,
    Checkin,
    Tasted,
)
from beers.api.pagination import Pagination, LargeResultPagination
from beers.api.serializers import (
    BeerSerializer,
    AuthenticatedBeerSerializer,
    StockSerializer,
    StoreSerializer,
    WrongMatchSerializer,
    ReleaseSerializer,
    StockChangeSerializer,
    AuthenticatedStockChangeSerializer,
)
from .utils import parse_bool


class StaffBrowsableMixin(object):
    def get_renderers(self):
        """
        Add Browsable API renderer if user is staff.
        """
        rends = self.renderer_classes
        if self.request.user and self.request.user.is_staff:
            rends.append(renderers.BrowsableAPIRenderer)
        return [renderer() for renderer in rends]


class BeerViewSet(StaffBrowsableMixin, ModelViewSet):
    pagination_class = LargeResultPagination
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
        "tasted__rating",
    ]
    filterset_class = BeerFilter

    def get_queryset(self):
        queryset = Beer.objects.all()
        beers = self.request.query_params.get("beers", None)
        user_checkin = self.request.query_params.get("user_checkin", None)
        user_tasted = self.request.query_params.get("user_tasted", None)
        user_wishlisted = self.request.query_params.get("user_wishlisted", None)
        if beers is not None:
            beers = list(int(v) for v in beers.split(","))
            queryset = queryset.filter(vmp_id__in=beers)
        if (
            user_checkin is not None
            and parse_bool(user_checkin)
            and self.request.user
            and self.request.user.is_authenticated
        ):
            queryset = queryset.filter(checkin__user=self.request.user)
        elif (
            user_checkin is not None
            and not parse_bool(user_checkin)
            and self.request.user
            and self.request.user.is_authenticated
        ):
            queryset = queryset.exclude(checkin__user=self.request.user)
        if (
            user_tasted is not None
            and parse_bool(user_tasted)
            and self.request.user
            and self.request.user.is_authenticated
        ):
            queryset = queryset.filter(tasted__user=self.request.user)
        elif (
            user_tasted is not None
            and not parse_bool(user_tasted)
            and self.request.user
            and self.request.user.is_authenticated
        ):
            queryset = queryset.exclude(tasted__user=self.request.user)
        if (
            user_wishlisted is not None
            and parse_bool(user_wishlisted)
            and self.request.user
            and self.request.user.is_authenticated
        ):
            print("test")
            queryset = queryset.filter(wishlist__user=self.request.user)
        elif (
            user_wishlisted is not None
            and not parse_bool(user_wishlisted)
            and self.request.user
            and self.request.user.is_authenticated
        ):
            print("teset")
            queryset = queryset.exclude(wishlist__user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_authenticated:
            return AuthenticatedBeerSerializer
        else:
            return BeerSerializer


class StockChangeViewSet(StaffBrowsableMixin, ModelViewSet):
    pagination_class = Pagination
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = StockChangeFilter

    def get_queryset(self):
        queryset = (
            Stock.objects.all()
            .exclude(Q(stocked_at=None) & Q(unstocked_at=None))
            .annotate(stock_unstock_at=Greatest("stocked_at", "unstocked_at"))
            .order_by(
                F("stock_unstock_at__date").desc(),
                F("stocked_at").desc(nulls_last=True),
            )
        )
        return queryset

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_authenticated:
            return AuthenticatedStockChangeSerializer
        else:
            return StockChangeSerializer


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


class ReleaseViewSet(StaffBrowsableMixin, ModelViewSet):
    queryset = (
        Release.objects.filter(active=True)
        .order_by("-release_date")
        .prefetch_related("beer")
        .annotate(
            product_count=Count("beer", distinct=True),
            beer_count=Count(
                "beer", filter=Q(beer__main_category__iexact="Øl"), distinct=True
            ),
            cider_count=Count(
                "beer", filter=Q(beer__main_category__iexact="Sider"), distinct=True
            ),
            mead_count=Count(
                "beer", filter=Q(beer__main_category__iexact="Mjød"), distinct=True
            ),
            product_selections=ArrayAgg("beer__product_selection", distinct=True),
        )
    )
    serializer_class = ReleaseSerializer
    pagination_class = Pagination
    permission_classes = [permissions.AllowAny]


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_checked_in_styles(request):
    try:
        user = request.user
        styles = list(
            Checkin.objects.filter(user=user)
            .order_by("style")
            .exclude(style__isnull=True)
            .values_list("style", flat=True)
            .distinct()
        )

        data = {"checked_in_styles": styles}
        return Response(data, status=200)
    except:
        message = {"message": "An error occurred"}
        return Response(message, status=500)


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def add_remove_tasted(request) -> Response:
    user = request.user
    beer_id = request.query_params.get("beer_id", None)
    rating = request.query_params.get("rating", None)

    if beer_id is None:
        message = {"message": "beer_id missing"}
        return Response(message, status=400)

    beers = []
    beers.append(Beer.objects.get(vmp_id=beer_id))
    if beers[0].untpd_id:
        beers = Beer.objects.filter(untpd_id=beers[0].untpd_id)
    if request.method == "POST":
        try:
            for beer in beers:
                tasted, _ = Tasted.objects.get_or_create(user=user, beer=beer)
                tasted.rating = rating
                tasted.save()
            message = {
                "message": f"{beer.vmp_name} marked as tasted with rating {rating}"
            }
            return Response(message, status=200)
        except Exception as e:
            message = {"message": str(e)}
            return Response(message, status=500)

    elif request.method == "DELETE":
        try:
            for beer in beers:
                Tasted.objects.get(user=user, beer=beer).delete()
            message = {"message": f"{beer.vmp_name} unmarked as tasted"}
            return Response(message, status=200)
        except Exception as e:
            message = {"message": str(e)}
            return Response(message, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_wishlist(request):
    beer_id = request.query_params.get("beer_id", None)
    if beer_id is not None:
        try:
            beer = Beer.objects.get(vmp_id=beer_id)
            wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
            if beer not in wishlist.beer.all():
                wishlist.beer.add(beer)
                message = {"message": "Beer added to wishlist"}
            else:
                message = {"message": "Beer already in wishlist"}
            return Response(message, status=200)
        except:
            message = {"message": "An error occurred"}
            return Response(message, status=500)
    else:
        message = {"message": "beer_id missing"}
        return Response(message, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_wishlist(request):
    beer_id = request.query_params.get("beer_id", None)
    if beer_id is not None:
        try:
            beer = Beer.objects.get(vmp_id=beer_id)
            wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
            if beer in wishlist.beer.all():
                wishlist.beer.remove(beer)
                message = {"message": "Beer removed from wishlist"}
            else:
                message = {"message": "Beer not in wishlist"}
            return Response(message, status=200)
        except:
            message = {"message": "An error occurred"}
            return Response(message, status=500)
    else:
        message = {"message": "beer_id missing"}
        return Response(message, status=400)

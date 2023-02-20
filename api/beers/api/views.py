from distutils.util import strtobool
from django.db.models import F, Q
from django.db.models.functions import Greatest
from rest_framework import permissions, filters, renderers
from rest_framework.views import APIView
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
from beers.models import Beer, Stock, Store, WrongMatch, Release, Wishlist, Checkin
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
    queryset = Release.objects.filter(active=True).order_by("-release_date")
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


class DeleteAccount(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            user = self.request.user
            user.delete()

            message = {"message": "User deleted"}
            return Response(message, status=200)
        except:
            message = {"message": "Failed to delete user"}
        return Response(message, status=400)

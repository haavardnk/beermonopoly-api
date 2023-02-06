from distutils.util import strtobool
from rest_framework import serializers
from beers.models import (
    Beer,
    Stock,
    Store,
    WrongMatch,
    Checkin,
    Badge,
    Wishlist,
    Release,
    FriendList,
)
from django.contrib.auth.models import User
from drf_dynamic_fields import DynamicFieldsMixin
from django.db.models import Avg, Count


class BeerSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="beer-detail")
    app_rating = serializers.SerializerMethodField("get_app_rating")
    badges = serializers.SerializerMethodField("get_badges")
    stock = serializers.SerializerMethodField("get_stock")
    all_stock = serializers.SerializerMethodField("get_all_stock")

    def get_app_rating(self, beer):
        ci = (
            User.objects.filter(checkin__beer=beer)
            .annotate(
                user_rating=Avg("checkin__rating"), user_count=Count("checkin__rating")
            )
            .aggregate(rating=Avg("user_rating"), count=Count("user_rating"))
        )

        serializer = AppRatingSerializer(instance=ci)
        return serializer.data

    def get_badges(self, beer):
        ci = Badge.objects.filter(beer=beer)
        serializer = BadgeSerializer(instance=ci, many=True)
        return serializer.data

    def get_stock(self, beer):
        store = self.context["request"].query_params.get("store")
        if store is not None and len(store.split(",")) < 2:
            try:
                ci = Stock.objects.get(beer=beer, store=store)
            except Stock.DoesNotExist:
                return None
        else:
            return None
        return ci.quantity

    def get_all_stock(self, beer):
        all_stock = self.context["request"].query_params.get("all_stock")
        if all_stock and bool(strtobool(all_stock)):
            try:
                ci = Stock.objects.filter(beer=beer).exclude(quantity=0)
                serializer = AllStockSerializer(instance=ci, many=True)
            except Stock.DoesNotExist:
                return None
        else:
            return None
        return serializer.data

    class Meta:
        model = Beer
        fields = [
            "url",
            "vmp_id",
            "untpd_id",
            "vmp_name",
            "untpd_name",
            "brewery",
            "country",
            "product_selection",
            "price",
            "volume",
            "price_per_volume",
            "abv",
            "ibu",
            "rating",
            "checkins",
            "main_category",
            "sub_category",
            "style",
            "description",
            "prioritize_recheck",
            "verified_match",
            "vmp_url",
            "untpd_url",
            "label_hd_url",
            "label_sm_url",
            "vmp_updated",
            "untpd_updated",
            "created_at",
            "app_rating",
            "badges",
            "stock",
            "all_stock",
            "post_delivery",
            "store_delivery",
            "year",
            "fullness",
            "sweetness",
            "freshness",
            "bitterness",
            "sugar",
            "acid",
            "color",
            "aroma",
            "taste",
            "storable",
            "food_pairing",
            "raw_materials",
            "method",
            "allergens",
        ]


class AuthenticatedBeerSerializer(BeerSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="beer-detail")
    user_checked_in = serializers.SerializerMethodField("get_checkins")
    friends_checked_in = serializers.SerializerMethodField("get_friends_checkins")
    app_rating = serializers.SerializerMethodField("get_app_rating")
    user_wishlisted = serializers.SerializerMethodField("get_wishlist")
    badges = serializers.SerializerMethodField("get_badges")
    stock = serializers.SerializerMethodField("get_stock")
    all_stock = serializers.SerializerMethodField("get_all_stock")

    def get_checkins(self, beer):
        ci = User.objects.filter(
            id=self.context["request"].user.id, checkin__beer=beer
        ).annotate(rating=Avg("checkin__rating"), count=Count("checkin__rating"))
        serializer = CheckinSerializer(instance=ci, many=True)
        return serializer.data

    def get_friends_checkins(self, beer):
        try:
            friends = FriendList.objects.get(user=self.context["request"].user)

            ci = friends.friend.filter(checkin__beer=beer).annotate(
                rating=Avg("checkin__rating"), count=Count("checkin__rating")
            )
            serializer = FriendCheckinSerializer(instance=ci, many=True)

        except FriendList.DoesNotExist:
            return None
        return serializer.data

    def get_app_rating(self, beer):
        ci = (
            User.objects.filter(checkin__beer=beer)
            .annotate(
                user_rating=Avg("checkin__rating"), user_count=Count("checkin__rating")
            )
            .aggregate(rating=Avg("user_rating"), count=Count("user_rating"))
        )

        serializer = AppRatingSerializer(instance=ci)
        return serializer.data

    def get_wishlist(self, beer):
        wishlist = Wishlist.objects.filter(user=self.context["request"].user, beer=beer)
        if wishlist:
            return True
        return False

    def get_badges(self, beer):
        ci = Badge.objects.filter(beer=beer)
        serializer = BadgeSerializer(instance=ci, many=True)
        return serializer.data

    def get_stock(self, beer):
        store = self.context["request"].query_params.get("store")
        if store is not None and len(store.split(",")) < 2:
            try:
                print(store)
                ci = Stock.objects.get(beer=beer, store=store)
            except Stock.DoesNotExist:
                return None
        else:
            return None
        return ci.quantity

    def get_all_stock(self, beer):
        all_stock = self.context["request"].query_params.get("all_stock")
        if all_stock and bool(strtobool(all_stock)):
            try:
                ci = Stock.objects.filter(beer=beer).exclude(quantity=0)
                serializer = AllStockSerializer(instance=ci, many=True)
            except Stock.DoesNotExist:
                return None
        else:
            return None
        return serializer.data

    class Meta:
        model = Beer
        fields = [
            "url",
            "vmp_id",
            "untpd_id",
            "vmp_name",
            "untpd_name",
            "brewery",
            "country",
            "product_selection",
            "price",
            "volume",
            "price_per_volume",
            "abv",
            "ibu",
            "rating",
            "checkins",
            "main_category",
            "sub_category",
            "style",
            "description",
            "prioritize_recheck",
            "verified_match",
            "vmp_url",
            "untpd_url",
            "label_hd_url",
            "label_sm_url",
            "vmp_updated",
            "untpd_updated",
            "created_at",
            "user_checked_in",
            "friends_checked_in",
            "app_rating",
            "user_wishlisted",
            "badges",
            "stock",
            "all_stock",
            "post_delivery",
            "store_delivery",
            "year",
            "fullness",
            "sweetness",
            "freshness",
            "bitterness",
            "sugar",
            "acid",
            "color",
            "aroma",
            "taste",
            "storable",
            "food_pairing",
            "raw_materials",
            "method",
            "allergens",
        ]


class AllStockSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(read_only=True, source="store.name")

    class Meta:
        model = Stock
        fields = ["store_name", "quantity"]


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["text"]


class CheckinSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField()
    count = serializers.IntegerField()

    class Meta:
        model = User
        fields = ["rating", "count"]


class FriendCheckinSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    rating = serializers.FloatField()
    count = serializers.IntegerField()

    class Meta:
        model = User
        fields = ["username", "rating", "count", "avatar"]

    def get_avatar(self, instance):
        avatar = instance.socialaccount_set.all()[0].extra_data["response"]["user"][
            "user_avatar"
        ]
        return avatar


class AppRatingSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField()
    count = serializers.IntegerField()

    class Meta:
        model = User
        fields = ["rating", "count"]


class StoreSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class StockSerializer(serializers.ModelSerializer):
    beer_name = serializers.CharField(read_only=True, source="beer.vmp_name")
    store_name = serializers.CharField(read_only=True, source="store.name")

    class Meta:
        model = Stock
        fields = [
            "beer",
            "beer_name",
            "store",
            "store_name",
            "quantity",
            "stock_updated",
        ]


class WrongMatchSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="wrongmatch-detail")
    beer_name = serializers.CharField(read_only=True, source="beer.vmp_name")
    current_untpd_url = serializers.CharField(read_only=True, source="beer.untpd_url")
    current_untpd_id = serializers.CharField(read_only=True, source="beer.untpd_id")

    class Meta:
        model = WrongMatch
        fields = [
            "url",
            "beer",
            "beer_name",
            "current_untpd_url",
            "current_untpd_id",
            "suggested_url",
        ]


class ReleaseSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    beer_count = serializers.SerializerMethodField("get_beer_count")

    def get_beer_count(self, release):
        beer_count = release.beer.all().count()
        return beer_count

    class Meta:
        model = Release
        fields = [
            "name",
            "active",
            "release_date",
            "beer_count",
            "product_selection",
            "beer",
        ]

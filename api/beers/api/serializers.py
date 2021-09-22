from rest_framework import serializers
from beers.models import Beer, Stock, Store, WrongMatch, Checkin, Badge
from drf_dynamic_fields import DynamicFieldsMixin


class BeerSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="beer-detail")
    badges = serializers.SerializerMethodField("get_badges")

    def get_badges(self, beer):
        ci = Badge.objects.filter(beer=beer)
        serializer = BadgeSerializer(instance=ci, many=True)
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
            "product_selection",
            "price",
            "volume",
            "abv",
            "ibu",
            "rating",
            "checkins",
            "sub_category",
            "style",
            "description",
            "prioritize_recheck",
            "verified_match",
            "vmp_url",
            "untpd_url",
            "label_url",
            "vmp_updated",
            "untpd_updated",
            "created_at",
            "badges",
        ]


class AuthenticatedBeerSerializer(BeerSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="beer-detail")
    user_checked_in = serializers.SerializerMethodField("get_checkins")
    badges = serializers.SerializerMethodField("get_badges")

    def get_checkins(self, beer):
        ci = Checkin.objects.filter(
            user=self.context["request"].user, beer=beer
        ).order_by("-checkin_id")[:1]
        serializer = CheckinSerializer(instance=ci, many=True)
        return serializer.data

    def get_badges(self, beer):
        ci = Badge.objects.filter(beer=beer)
        serializer = BadgeSerializer(instance=ci, many=True)
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
            "product_selection",
            "price",
            "volume",
            "abv",
            "ibu",
            "rating",
            "checkins",
            "sub_category",
            "style",
            "description",
            "prioritize_recheck",
            "verified_match",
            "vmp_url",
            "untpd_url",
            "label_url",
            "vmp_updated",
            "untpd_updated",
            "created_at",
            "user_checked_in",
            "badges",
        ]


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["text"]


class CheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkin
        fields = ["checkin_id", "rating", "checkin_url"]


class StoreSerializer(serializers.ModelSerializer):
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


class MatchSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="match-detail")

    class Meta:
        model = Beer
        fields = [
            "url",
            "vmp_name",
            "untpd_url",
        ]

    def update(self, instance, validated_data):
        instance.vmp_name = self.validated_data["vmp_name"]
        instance.untpd_url = self.validated_data["untpd_url"]
        instance.untpd_id = instance.untpd_url.split("/")[-1]
        instance.prioritize_recheck = True
        instance.verified_match = True
        instance.match_manually = False
        instance.save()
        return instance


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

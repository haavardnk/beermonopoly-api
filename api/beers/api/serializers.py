from rest_framework import serializers
from beers.models import Beer, Stock, Store
from drf_dynamic_fields import DynamicFieldsMixin


class BeerSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Beer
        fields = [
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
            "vmp_url",
            "untpd_url",
            "label_url",
            "vmp_updated",
            "untpd_updated",
            "prioritize_recheck",
            "created_at",
        ]


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

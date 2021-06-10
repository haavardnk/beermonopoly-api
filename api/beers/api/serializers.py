from rest_framework import serializers
from beers.models import Beer, Stock, Store


class BeerSerializer(serializers.ModelSerializer):
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

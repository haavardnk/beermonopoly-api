from rest_framework import serializers
from beers.models import Beer, Stock, Store

class BeerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Beer
        exclude = ("verified_match", "prioritize_recheck", "match_manually", "active")

class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Store
        fields = "__all__"

class StockSerializer(serializers.ModelSerializer):
    beer_name = serializers.CharField(read_only=True, source="beer.vmp_name")
    store_name = serializers.CharField(read_only=True, source="store.name")


    class Meta:
        model = Stock
        fields = ["beer", "beer_name", "store", "store_name", "quantity"]
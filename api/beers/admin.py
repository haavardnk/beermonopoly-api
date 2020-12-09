from django.contrib import admin
from beers.models import Beer, ExternalAPI, Store, Stock

@admin.register(Beer)
class BeerAdmin(admin.ModelAdmin):
    list_display = ("vmp_name", "brewery","main_category", "vmp_id", "untpd_id", "rating", "vmp_updated", "untpd_updated")

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "storeid", "address")

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("store", "beer", "quantity")

admin.site.register(ExternalAPI)

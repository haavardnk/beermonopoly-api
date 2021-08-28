from django.contrib import admin
from beers.models import (
    Beer,
    ExternalAPI,
    Store,
    Stock,
    MatchFilter,
    WrongMatch,
    VmpNotReleased,
    Checkin,
)


@admin.register(Beer)
class BeerAdmin(admin.ModelAdmin):
    list_display = (
        "vmp_name",
        "brewery",
        "untpd_name",
        "vmp_id",
        "untpd_id",
        "rating",
        "checkins",
        "vmp_updated",
        "untpd_updated",
        "match_manually",
        "active",
    )
    search_fields = ("vmp_name", "brewery", "vmp_id", "untpd_id", "style")


class StockInline(admin.TabularInline):
    model = Stock


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "store_id", "address", "store_updated")
    inlines = [StockInline]
    search_fields = ("name", "store_id")


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("store", "beer", "quantity", "stock_updated")
    search_fields = ("store__name", "beer__vmp_name")


admin.site.register(Checkin)
admin.site.register(ExternalAPI)
admin.site.register(MatchFilter)
admin.site.register(WrongMatch)
admin.site.register(VmpNotReleased)

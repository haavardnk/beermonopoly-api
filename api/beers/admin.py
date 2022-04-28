from django.contrib import admin
from beers.models import (
    Option,
    Beer,
    ExternalAPI,
    Store,
    Stock,
    WrongMatch,
    VmpNotReleased,
    Checkin,
    Badge,
    Wishlist,
    FriendList,
    Release,
)


@admin.register(Beer)
class BeerAdmin(admin.ModelAdmin):
    list_display = (
        "vmp_name",
        "main_category",
        "untpd_name",
        "vmp_id",
        "untpd_id",
        "rating",
        "checkins",
        "vmp_updated",
        "untpd_updated",
        "created_at",
        "match_manually",
        "active",
    )
    search_fields = ("vmp_name", "brewery", "vmp_id", "untpd_id", "style")


class MatchManually(Beer):
    class Meta:
        proxy = True


@admin.register(MatchManually)
class MatchManallyAdmin(BeerAdmin):
    list_display = (
        "vmp_name",
        "untpd_name",
        "vmp_id",
        "untpd_id",
        "match_manually",
        "active",
    )
    fields = (
        "vmp_name",
        "untpd_url",
    )

    def get_queryset(self, request):
        return self.model.objects.filter(match_manually=True, active=True)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "store_id", "address", "store_updated")
    search_fields = ("name", "store_id")


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("store", "beer", "quantity", "stock_updated")
    search_fields = ("store__name", "beer__vmp_name")


class CheckinBeersInline(admin.TabularInline):
    model = Checkin.beer.through


@admin.register(Checkin)
class CheckinAdmin(admin.ModelAdmin):
    inlines = [
        CheckinBeersInline,
    ]
    exclude = ["beer"]
    list_display = ("checkin_id", "get_beers", "untpd_id", "user")
    search_fields = (
        "checkin_id",
        "untpd_id",
        "user__username",
        "beer__vmp_name",
    )

    def get_beers(self, obj):
        return "\n".join([p.vmp_name for p in obj.beer.all()])


class WishlistBeersInline(admin.TabularInline):
    model = Wishlist.beer.through


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    inlines = [
        WishlistBeersInline,
    ]
    exclude = ["beer"]
    list_display = (
        "user",
        "get_beers",
    )

    def get_beers(self, obj):
        return "\n".join([p.vmp_name for p in obj.beer.all()])


class FriendListFriendsInline(admin.TabularInline):
    model = FriendList.friend.through


@admin.register(FriendList)
class FriendListAdmin(admin.ModelAdmin):
    inlines = [
        FriendListFriendsInline,
    ]
    list_display = (
        "user",
        "get_friends",
    )

    def get_friends(self, obj):
        return "\n".join([f.username for f in obj.friend.all()])


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(Option)
admin.site.register(Badge)
admin.site.register(ExternalAPI)
admin.site.register(WrongMatch)
admin.site.register(VmpNotReleased)

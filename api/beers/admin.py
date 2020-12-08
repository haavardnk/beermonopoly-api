from django.contrib import admin
from beers.models import Beer, SiteSetting

@admin.register(Beer)
class BeerAdmin(admin.ModelAdmin):
    list_display = ("name", "beerid", "untappd_id", "rating", "vinmonopolet_updated", "untappd_updated")

admin.site.register(SiteSetting)

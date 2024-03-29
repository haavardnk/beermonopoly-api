from django.contrib import admin
from notifications.models import FCMToken


@admin.register(FCMToken)
class FCMTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token")

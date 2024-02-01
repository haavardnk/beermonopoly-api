from django.urls import re_path
from notifications.api.views import set_token

urlpatterns = [
    re_path(r"set_token", set_token, name="set_token"),
]

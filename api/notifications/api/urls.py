from django.conf.urls import url
from notifications.api.views import set_token

urlpatterns = [
    url(r"set_token", set_token, name="set_token"),
]

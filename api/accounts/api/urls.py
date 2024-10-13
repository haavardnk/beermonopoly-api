from accounts.api.views import DeleteAccount, apple_signin_callback
from django.urls import include, path


urlpatterns = [
    path("_allauth/", include("allauth.headless.urls")),
    path("accounts/", include("allauth.urls")),
    path("accounts/apple/login/callback2/", apple_signin_callback),
    path("accounts/delete/", DeleteAccount.as_view(), name="rest_delete"),
]

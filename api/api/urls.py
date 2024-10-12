from django.contrib import admin
from django.urls import include, path, re_path
from api.views import DeleteAccount, apple_signin_callback


urlpatterns = [
    re_path(r"^admin/shell/", include("django_admin_shell.urls")),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("", include("beers.api.urls")),
    path("auth/delete/", DeleteAccount.as_view(), name="rest_delete"),
    path("notifications", include("notifications.api.urls")),
    path("accounts/", include("allauth.urls")),
    path("_allauth/", include("allauth.headless.urls")),
    path("accounts/apple/login/callback2/", apple_signin_callback),
]

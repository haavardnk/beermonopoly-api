from django.urls import path, re_path, include
from accounts.views import EmailConfirmedTemplateView

from allauth.account.views import (
    confirm_email,
    password_reset_from_key,
    password_reset_from_key_done,
)

urlpatterns = [
    path("", include("accounts.api.urls")),
    re_path(
        r"^confirm-email/(?P<key>[-:\w]+)/$",
        confirm_email,
        name="account_confirm_email",
    ),
    path(
        "email-confirmed/",
        EmailConfirmedTemplateView.as_view(),
        name="account_email_confirmed",
    ),
    re_path(
        r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        password_reset_from_key,
        name="account_reset_password_from_key",
    ),
    path(
        "password/reset/key/done/",
        password_reset_from_key_done,
        name="account_reset_password_from_key_done",
    ),
]

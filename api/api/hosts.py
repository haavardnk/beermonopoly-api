from django_hosts import patterns, host
from django.conf import settings

host_patterns = patterns(
    "",
    host(r"api", settings.ROOT_URLCONF, name="api"),
    host(r"auth", "accounts.urls", name="auth"),
)

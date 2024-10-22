import os
import json
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dummykey")
DEBUG = int(os.getenv("DEBUG_VALUE", 1))
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "api.localhost,auth.localhost").split(
    ","
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django.contrib.sites",
    "rest_framework",
    "rest_framework.authtoken",
    "django_q",
    "django_filters",
    "django_extensions",
    "django_hosts",
    "django_admin_shell",
    "accounts",
    "beers",
    "notifications",
    "corsheaders",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.untappd",
    "allauth.socialaccount.providers.apple",
    "allauth.socialaccount.providers.google",
    "allauth.headless",
    "anymail",
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


HEADLESS_TOKEN_STRATEGY = "api.token.AccessTokenStrategy"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_SESSION_REMEMBER = True


SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_STORE_TOKENS = True

SOCIALACCOUNT_PROVIDERS = {
    "untappd": {
        "USER_AGENT": "django:Beermonopoly",
    },
    "apple": {
        "APPS": [
            {
                "client_id": os.getenv("APPLE_AUTH_CLIENT_ID_APPLE"),
                "secret": os.getenv("APPLE_AUTH_SECRET"),
                "key": os.getenv("APPLE_AUTH_KEY"),
                "settings": {
                    "certificate_key": os.getenv("APPLE_AUTH_CERTIFICATE_KEY"),
                    "hidden": True,
                },
            },
            {
                "client_id": os.getenv("APPLE_AUTH_CLIENT_ID_ANDROID"),
                "secret": os.getenv("APPLE_AUTH_SECRET"),
                "key": os.getenv("APPLE_AUTH_KEY"),
                "settings": {
                    "certificate_key": os.getenv("APPLE_AUTH_CERTIFICATE_KEY"),
                },
            },
        ]
    },
    "google": {
        "AUTH_PARAMS": {
            "access_type": "offline",
        },
        "OAUTH_PKCE_ENABLED": True,
    },
}

ANYMAIL = {
    "MAILGUN_API_KEY": os.getenv("MAILGUN_API_KEY"),
    "MAILGUN_SENDER_DOMAIN": os.getenv("MAILGUN_SENDER_DOMAIN"),
    "MAILGUN_API_URL": os.getenv("MAILGUN_API_URL"),
}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
SERVER_EMAIL = os.getenv("SERVER_EMAIL")


MIDDLEWARE = [
    "django_hosts.middleware.HostsRequestMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_hosts.middleware.HostsResponseMiddleware",
]

ROOT_URLCONF = "api.urls"
ROOT_HOSTCONF = "api.hosts"
DEFAULT_HOST = "api"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "api.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.{}".format(
            os.getenv("DATABASE_ENGINE", "postgresql")
        ),
        "NAME": os.getenv("DATABASE_NAME", "beerdb"),
        "USER": os.getenv("DATABASE_USERNAME", "beer"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "123123"),
        "HOST": os.getenv("DATABASE_HOST", "127.0.0.1"),
        "PORT": os.getenv("DATABASE_PORT", 5432),
        "OPTIONS": json.loads(os.getenv("DATABASE_OPTIONS", "{}")),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Paris"

USE_I18N = True


USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


STATIC_ROOT = "/static2"
STATIC_URL = "/static2/"

Q_CLUSTER = {
    "name": "beerapi",
    "orm": "default",
    "timeout": 3600,
    "retry": 4000,
    "save_limit": 50,
    "save_limit_per": "func",
    "ack_failures": True,
    "catch_up": False,
    "recycle": 10,
    "cpu_affinity": 1,
    "max_attempts": 1,
    "attempt_count": 1,
    "label": "Django Q",
    "error_reporter": {
        "sentry": {
            "dsn": "https://6d8c8869d8c64767b26de850f794bc4c@o985007.ingest.sentry.io/5941029"
        }
    },
}

CORS_ALLOWED_ORIGINS = [
    "https://www.vinmonopolet.no",
    "https://app.vinmonopolet.no",
    "https://olmonopolet.app",
    "https://www.olmonopolet.app",
]
CORS_ALLOW_METHODS = [
    "GET",
]
CSRF_TRUSTED_ORIGINS = [
    "https://api.beermonopoly.com",
    "https://auth.beermonopoly.com",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

NOTEBOOK_ARGUMENTS = [
    "--ip",
    "0.0.0.0",
    "--port",
    "8888",
    "--allow-root",
    "--no-browser",
]

IPYTHON_ARGUMENTS = [
    "--ext",
    "django_extensions.management.notebook_extension",
]

if not DEBUG:
    sentry_sdk.init(
        dsn="https://6d8c8869d8c64767b26de850f794bc4c@o985007.ingest.sentry.io/5941029",
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.2,
        send_default_pii=True,
    )

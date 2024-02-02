"""
Django settings for api project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
import json
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dummykey")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.getenv("DEBUG_VALUE", 1))

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(",")


# Application definition

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
    "beers",
    "notifications",
    "corsheaders",
    "dj_rest_auth.registration",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.untappd",
    "django_admin_shell",
]

SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    "untappd": {
        "USER_AGENT": "django:Beermonopoly",
    }
}

SOCIALACCOUNT_STORE_TOKENS = True

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "api.urls"

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
    "recycle": 100,
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
]

if "TRAVIS" in os.environ:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "travisci",
            "USER": "postgres",
            "PASSWORD": "",
            "HOST": "localhost",
            "PORT": "",
        }
    }

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

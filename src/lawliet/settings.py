"""
Django settings for lawliet project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import logging
import os
import dotenv
import uuid
from base64 import b64encode

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)

# Read from .env file, if it exists
dotenv_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
if os.environ.setdefault("DEVELOPMENT", "").lower() == "yes":
    logging.warn("Running server in debug mode")
    DEBUG = True
else:
    logging.warn("Running server in production mode")
    DEBUG = False

if not DEBUG and "HOST" not in os.environ:
    raise Exception("HOST environmental variable must be defined if DEBUG is False.")


# SECURITY WARNING: keep the secret key used in production secret!
#
# If DJANGO_SECRET_KEY is undefined or doesn't exist as an environmental
# variable, and DEBUG is True, we generate a randomized 128-bit key.
if "DJANGO_SECRET_KEY" in os.environ:
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
elif DEBUG:
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", b64encode(uuid.uuid4().bytes))
else:
    raise Exception("DJANGO_SECRET_KEY must be defined in DEBUG is False.")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", None)
if ALLOWED_HOSTS:
    ALLOWED_HOSTS = ALLOWED_HOSTS.strip().replace(" ", "").split(",")
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
    "dashboard",
    "labs",
    "users",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lawliet.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Store templates in assets/templates/
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "lawliet.wsgi.application"

# Change the form renderer so that we can use custom widget templates
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
ENGINE = os.getenv("DATABASE_ENGINE", "sqlite3")
if ENGINE == "sqlite3":
    logging.info("Using SQLite database...")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
elif ENGINE == "mysql":
    logging.info("Using MySQL database...")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("MYSQL_DATABASE", None),
            "USER": os.getenv("MYSQL_USER", None),
            "PASSWORD": os.getenv("MYSQL_PASSWORD", None),
            "HOST": os.getenv("DATABASE_HOST", "localhost"),
            "PORT": "3306",
        }
    }
else:
    raise Exception("Environmental variable 'ENGINE' must be either sqlite3 or mysql")


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Directory in which to store user files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "assets")]

# Authentication options

LOGIN_URL = "/login"

# Email parameters

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = bool(os.getenv("EMAIL_USE_TLS", True))

# Additional parameters

MAX_PASSWORD_LENGTH = int(os.getenv("MAX_PASSWORD_LENGTH", 64))
MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", 8))

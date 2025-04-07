"""
Django settings for ecommerce project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # Default to 'development' if not set


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "templates"
STATIC_DIR = os.path.join(BASE_DIR,'static')

# Media settings
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
MEDIA_ROOT = MEDIA_DIR  # Use MEDIA_DIR here


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-p+r28mh==e(rshl-ku@$7(fv!x9r_ja)i*(g_c1+g_zc(lc8ac"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
WHITENOISE_USE_FINDERS = True
ALLOWED_HOSTS = [ 'localhost', '127.0.0.1','django-ecommerce-138p.onrender.com']


CSRF_TRUSTED_ORIGINS = ['https://django-ecommerce-138p.onrender.com']

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django_countries",
    "django.contrib.staticfiles",
    "core",
    "accounts",
    "payment",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]

ROOT_URLCONF = "ecommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMP_DIR],
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

WSGI_APPLICATION = "ecommerce.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": str(os.path.join(BASE_DIR, "db.sqlite3")),
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'postgres',       # The name of your PostgreSQL database
#         'USER': 'postgres',       # The PostgreSQL username
#         'PASSWORD': 'postgres',  # The PostgreSQL password
#         'HOST': 'localhost',           # Change this if your database is hosted elsewhere
#         'PORT': '5432',               # Default PostgreSQL port
#     }
# }

import dj_database_url

DATABASES = {}

if os.getenv("DATABASE_URL"):
    print("Using DATABASE_URL")
    DATABASES["default"] = dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True
    )
else:
    # Fallback to SQLite for development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [STATIC_DIR,]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = '/media/'



# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# django_heroku.settings(locals())
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Use your email service's SMTP server
EMAIL_PORT = 587  # Port for TLS, use 465 for SSL
EMAIL_USE_TLS = True  # Use TLS for encryption
EMAIL_HOST_USER = 'rochaksulu2002@gmail.com'  # Your email address
EMAIL_HOST_PASSWORD = 'oibf zeri qcyv yuep '  # Your email password (consider using environment variables for security)
DEFAULT_FROM_EMAIL = 'rochaksulu2002@gmail.com'  # Default "from" email address

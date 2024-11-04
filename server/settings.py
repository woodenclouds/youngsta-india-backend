from pathlib import Path
from datetime import timedelta
import os
import sys
import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent
env.read_env(os.path.join(BASE_DIR, ".env"))
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", False)
ENCRYPT_KEY = env("ENCRYPT_KEY")
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = [
    "rest_framework",
    "corsheaders",
    "drf_yasg",
    "storages",
    # 'colorfield',
    # 'colorfield',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main",
    "accounts",
    "payments",
    "products",
    "activities",
    "marketing",
    "adds",
]

DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

STRIPE_PUBLIC_KEY = "pk_test_51Oaup0SCFDYyAdrcmJjvocXMEBiN1ZIVTHegkD8RaJp3k9bYHatR6mwYUnILOaZ7i9psCnIFuLGTe65TEfiFedw800stdQ7wsL"
STRIPE_SECRET_KEY = "sk_test_51Oaup0SCFDYyAdrcg7lLPLt9INSIB0nhkgqqRkcuGAMdw3BdoXk8d2CefYDvHjQT6quKMEX9btjqNP6f5OCEp4xc009Z9Okfuk"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=env.int("ACCESS_TOKEN_LIFETIME")),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("REFRESH_TOKEN_LIFETIME")),
}

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = "server.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # "DIRS": [],
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


WSGI_APPLICATION = "server.wsgi.application"
if "watchman" in sys.argv:
    del sys.argv[1]
# DATABASES = {"default": env.db()}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
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
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024

AWS_STORAGE_BUCKET_NAME = "youngsta"
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_S3_REGION_NAME = "eu-north-1"  # e.g., 'us-west-1'

# Media files (uploaded by users)
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_URL = "/static/"
STATIC_FILE_ROOT = os.path.join(BASE_DIR, "static")
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, "static")
if not DEBUG:
    STATIC_ROOT = os.path.join("static")

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# CASHFREE_APP_ID = "TEST10152344375607512638f6aa3f7744325101"
CASHFREE_APP_ID = "TEST38551658fbc62a3493bfa982a2615583"
# CASHFREE_SECRET = "cfsk_ma_test_a9347840c047c564400988bfaaa66139_c3bc2f29"
CASHFREE_SECRET = "TEST13e388b7717db010f9e5e864679da34fea830bb3"
CASH_FREE_END_POINT = "https://sandbox.cashfree.com/pg"
CASH_FREE_X_API_VERSION = "https://api.cashfree.com/pg"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

RAZORPAY_KEY_ID = "rzp_test_katoK4CLT1zn9N"
RAZORPAY_KEY_SECRET = "pK0H9yzr9qC8WuD3DWMsjfb1"

SHIPROCKET_EMAIL = "youngstatech@gmail.com"
SHIPROCKET_PASSWORD = "QduVuBKQ9YNy*Wy"


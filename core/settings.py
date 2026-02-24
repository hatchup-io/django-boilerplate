import os
import sys
from pathlib import Path

from dotenv import load_dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment from .env if present (for MinIO creds, etc.)
load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-&6^0-uxgjdw+b$bbgt2wk+umahqh=)tqhu^ei(4q7oyo^gm(^u"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = [host for host in os.getenv("ALLOWED_HOSTS", "").split(",") if host]
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "storages",
    "django_jsonform",
    "django_ckeditor_5",
    "django_filters",
    "rest_framework",
    "drf_spectacular",
    "common.apps.CommonConfig",
    "users.apps.UsersConfig",
    "auth.apps.AuthConfig",
    "notification.apps.NotificationConfig",
    "document.apps.DocumentConfig",
]

# Custom user model
AUTH_USER_MODEL = "users.User"

# Auth backends
AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# Cache is used by role checks (short TTL) and request-scoped permission checks.
# Prefer Redis when available; fall back to local memory for dev environments.
REDIS_URL = os.getenv("REDIS_URL", "").strip()

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True,
            },
            "KEY_PREFIX": "hatchup",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "hatchup-auth",
        }
    }

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

_IS_TEST_RUN = "pytest" in " ".join(sys.argv) or (len(sys.argv) > 1 and sys.argv[1] == "test")

if _IS_TEST_RUN:
    _test_db_name = os.getenv("TEST_DB_NAME", os.getenv("DB_NAME", "postgres"))
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _test_db_name,
            "USER": os.getenv("TEST_DB_USER", os.getenv("DB_USER", "postgres")),
            "PASSWORD": os.getenv("TEST_DB_PASSWORD", os.getenv("DB_PASSWORD", "postgres")),
            "HOST": os.getenv("TEST_DB_HOST", os.getenv("DB_HOST", "localhost")),
            "PORT": os.getenv("TEST_DB_PORT", os.getenv("DB_PORT", "5432")),
            "TEST": {"NAME": _test_db_name},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "postgres"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
DATABASES["default"]["ATOMIC_REQUESTS"] = True


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"

# Email (for OTP, notifications)
if _IS_TEST_RUN:
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    OTP_EMAIL_ASYNC_SEND = False
else:
    EMAIL_BACKEND = os.getenv(
        "EMAIL_BACKEND",
        "django.core.mail.backends.console.EmailBackend",
    )
    OTP_EMAIL_ASYNC_SEND = os.getenv("OTP_EMAIL_ASYNC_SEND", "true").lower() in (
        "true",
        "1",
        "yes",
    )
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default local media (used when MinIO env vars aren't set)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Media storage (RustFS via S3-compatible API)
# Set these in `.env`:
# - RUSTFS_ENDPOINT=localhost:9000
# - RUSTFS_ACCESS_KEY=...
# - RUSTFS_SECRET_KEY=...
# - RUSTFS_BUCKET_NAME=...
# - RUSTFS_USE_HTTPS=false
RUSTFS_ENDPOINT = os.getenv("RUSTFS_ENDPOINT", "")
RUSTFS_USE_HTTPS = os.getenv("RUSTFS_USE_HTTPS", "false").lower() == "true"
AWS_S3_USE_SSL = RUSTFS_USE_HTTPS

AWS_ACCESS_KEY_ID = os.getenv("RUSTFS_ACCESS_KEY", "")
AWS_SECRET_ACCESS_KEY = os.getenv("RUSTFS_SECRET_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("RUSTFS_BUCKET_NAME", "")
AWS_S3_REGION_NAME = os.getenv("RUSTFS_REGION", "us-east-1")
AWS_S3_ENDPOINT_URL = (
    f"{'https' if RUSTFS_USE_HTTPS else 'http'}://{RUSTFS_ENDPOINT}"
    if RUSTFS_ENDPOINT
    else None
)
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_ADDRESSING_STYLE = "path"
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

_RUSTFS_READY = bool(
    RUSTFS_ENDPOINT
    and AWS_STORAGE_BUCKET_NAME
    and AWS_ACCESS_KEY_ID
    and AWS_SECRET_ACCESS_KEY
)

if _RUSTFS_READY:
    _S3_OPTIONS = {
        "access_key": AWS_ACCESS_KEY_ID,
        "secret_key": AWS_SECRET_ACCESS_KEY,
        "bucket_name": AWS_STORAGE_BUCKET_NAME,
        "endpoint_url": AWS_S3_ENDPOINT_URL,
        "region_name": AWS_S3_REGION_NAME,
        "addressing_style": AWS_S3_ADDRESSING_STYLE,
    }
    _S3_OPTIONS = {k: v for k, v in _S3_OPTIONS.items() if v}

    _RUSTFS_BASE_URL = AWS_S3_ENDPOINT_URL.rstrip("/")
    MEDIA_URL = f"{_RUSTFS_BASE_URL}/{AWS_STORAGE_BUCKET_NAME}/media/"
    STATIC_URL = f"{_RUSTFS_BASE_URL}/{AWS_STORAGE_BUCKET_NAME}/static/"

    STORAGES = {
        "default": {
            "BACKEND": "core.storages.MediaStorage",
            "OPTIONS": _S3_OPTIONS,
        },
        "staticfiles": {
            "BACKEND": "core.storages.StaticStorage",
            "OPTIONS": _S3_OPTIONS,
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": MEDIA_ROOT, "base_url": MEDIA_URL},
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

from .packages import REST_FRAMEWORK  # noqa: E402
from .packages.cors import *  # noqa: E402, F403
from .packages.simple_jwt import SIMPLE_JWT  # noqa: E402
from .packages.sentry import init_sentry  # noqa: E402

init_sentry(environment=ENVIRONMENT)

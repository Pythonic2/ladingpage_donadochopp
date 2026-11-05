from pathlib import Path
import os

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Ambiente: 'production' ou 'development'
ENVIRONMENT = os.environ.get("DJANGO_ENV", "development")
BUILD_STATICFILES = os.environ.get("BUILD_STATICFILES", "false").lower() in (
    "1",
    "true",
    "yes",
)
DATABASE_ENGINE = os.environ.get("DB_ENGINE", "").lower()
USE_POSTGRESQL = ENVIRONMENT == "production" or DATABASE_ENGINE in (
    "postgres",
    "postgresql",
)


def _list_from_env(name, default):
    value = os.environ.get(name)
    if not value:
        return default
    items = [item.strip() for item in value.split(",") if item.strip()]
    return list(dict.fromkeys([*default, *items]))

SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if ENVIRONMENT == "production":
        raise RuntimeError("SECRET_KEY is required in production")
    SECRET_KEY = "dev-secret-key-change-me"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENVIRONMENT == "development"
SERVE_MEDIA = os.environ.get("SERVE_MEDIA", "false").lower() in ("1", "true", "yes")

if ENVIRONMENT == "production":
    ALLOWED_HOSTS = _list_from_env("ALLOWED_HOSTS", [
        ".run.app",
        "vendas.donadochopp.com.br",
    ])
    ALLOWED_HOSTS = _list_from_env("DJANGO_ALLOWED_HOSTS", ALLOWED_HOSTS)
    CSRF_TRUSTED_ORIGINS = _list_from_env("CSRF_TRUSTED_ORIGINS", [
        "https://*.run.app",
        "https://vendas.donadochopp.com.br",
    ])
    CSRF_TRUSTED_ORIGINS = _list_from_env(
        "DJANGO_CSRF_TRUSTED_ORIGINS", CSRF_TRUSTED_ORIGINS
    )
else:
    ALLOWED_HOSTS = _list_from_env("DJANGO_ALLOWED_HOSTS", [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "vendas.donadochopp.com.br",
        "192.168.1.7",
    ])
    CSRF_TRUSTED_ORIGINS = _list_from_env("DJANGO_CSRF_TRUSTED_ORIGINS", [
        "http://localhost",
        "http://127.0.0.1",
        "https://vendas.donadochopp.com.br",
        "http://192.168.1.7:8010",
    ])

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = (
    os.environ.get("DJANGO_SECURE_SSL_REDIRECT", str(ENVIRONMENT == "production"))
    .lower()
    in ("1", "true", "yes")
)
SESSION_COOKIE_SECURE = ENVIRONMENT == "production"
CSRF_COOKIE_SECURE = ENVIRONMENT == "production"
SECURE_CONTENT_TYPE_NOSNIFF = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ckeditor",
    "home",
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

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

if USE_POSTGRESQL:
    db_schema = os.environ.get("DB_SCHEMA", "ladingpageddc")
    db_host = os.environ.get("DB_HOST")
    required_db_vars = ("DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST")
    missing_db_vars = [name for name in required_db_vars if not os.environ.get(name)]
    if missing_db_vars:
        raise RuntimeError(
            "Missing required PostgreSQL database variables: "
            + ", ".join(missing_db_vars)
        )

    db_options = {
        "connect_timeout": int(os.environ.get("DB_CONNECT_TIMEOUT", "10")),
        "sslmode": os.environ.get("DB_SSLMODE", "require"),
    }
    channel_binding = os.environ.get("DB_CHANNEL_BINDING")
    if channel_binding:
        db_options["channel_binding"] = channel_binding
    if db_schema and db_schema != "public" and "-pooler." not in db_host:
        db_options["options"] = f"-c search_path={db_schema}"

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.environ["DB_PASSWORD"],
            "HOST": db_host,
            "PORT": os.environ.get("DB_PORT", "5432"),
            "OPTIONS": db_options,
            "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", "60")),
            "CONN_HEALTH_CHECKS": True,
            "DISABLE_SERVER_SIDE_CURSORS": "-pooler." in db_host,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.environ.get("SQLITE_NAME", BASE_DIR / "db.sqlite3"),
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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = os.environ.get("STATIC_URL", "/static/")
STATIC_ROOT = os.environ.get("STATIC_ROOT", os.path.join(BASE_DIR, "staticfiles"))

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", os.path.join(BASE_DIR, "media"))

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "landing-page-ddc-cache",
        "TIMEOUT": None,
        "OPTIONS": {
            "MAX_ENTRIES": 5000,
        },
    }
}

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if ENVIRONMENT == "production" or BUILD_STATICFILES
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}

GCS_ENABLED = os.environ.get("GCS_ENABLED", "false").lower() in ("1", "true", "yes")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "")
GCS_PROJECT_ID = os.environ.get("GCS_PROJECT_ID", "")
GCS_APP_PREFIX = os.environ.get("GCS_APP_PREFIX", "landing-page-ddc").strip("/")
GCS_MEDIA_PREFIX = f"{GCS_APP_PREFIX}/midias"
GCS_SIGNED_URL_TTL = min(
    int(os.environ.get("GCS_SIGNED_URL_TTL", "604800")),
    604800,
)
GCS_SIGNED_URL_CACHE_TTL = min(
    int(os.environ.get("GCS_SIGNED_URL_CACHE_TTL", str(GCS_SIGNED_URL_TTL - 300))),
    max(GCS_SIGNED_URL_TTL - 60, 1),
)
GCS_IAM_SIGN_BLOB = os.environ.get("GCS_IAM_SIGN_BLOB", "false").lower() in (
    "1",
    "true",
    "yes",
)
GCS_SA_EMAIL = os.environ.get("GCS_SA_EMAIL", "")
MEDIA_MAX_UPLOAD_SIZE = int(os.environ.get("MEDIA_MAX_UPLOAD_SIZE", str(25 * 1024 * 1024)))

if GCS_ENABLED:
    missing_gcs_vars = [
        name
        for name, value in (
            ("GCS_BUCKET_NAME", GCS_BUCKET_NAME),
            ("GCS_PROJECT_ID", GCS_PROJECT_ID),
            ("GCS_APP_PREFIX", GCS_APP_PREFIX),
        )
        if not value
    ]
    if missing_gcs_vars:
        raise RuntimeError(
            "Missing required GCS variables: " + ", ".join(missing_gcs_vars)
        )

    STORAGES["default"] = {
        "BACKEND": "home.gcs_storage.CachedGoogleCloudStorage",
        "OPTIONS": {
            "bucket_name": GCS_BUCKET_NAME,
            "project_id": GCS_PROJECT_ID,
            "location": GCS_MEDIA_PREFIX,
            "default_acl": None,
            "querystring_auth": True,
            "expiration": GCS_SIGNED_URL_TTL,
            "file_overwrite": False,
            "iam_sign_blob": GCS_IAM_SIGN_BLOB,
            "sa_email": GCS_SA_EMAIL or None,
            "object_parameters": {
                "cache_control": "private, max-age=604800, immutable",
            },
        },
    }
# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

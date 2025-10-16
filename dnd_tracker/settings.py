"""
Django Settings for D&D Tracker Project

This module contains all Django settings for the D&D Tracker application.
It configures database connections, security settings, authentication,
static files, and application-specific settings.

Key Features:
- PostgreSQL database configuration
- Custom User model with 2FA support
- Environment variable management
- Security settings for production
- Static file configuration
- Session and CSRF settings
"""

from pathlib import Path
import os
from re import split
from dotenv import load_dotenv
import dj_database_url

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# SECURITY SETTINGS
# =============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Allowed hosts for production deployment
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

# Django applications installed in this project
INSTALLED_APPS = [
    # Django core applications
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Project applications
    "dnd_tracker",  # Main project app
    "accounts",  # User authentication and account management
    "campaigns",  # D&D campaign management
    "players",  # Player character management
    "monsters",  # Monster database management
    "game_sessions",  # Game session management
    "combat_tracker",  # Combat encounter tracking
]

# Middleware classes for request/response processing
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.security.SecurityHeadersMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Root URL configuration
ROOT_URLCONF = "dnd_tracker.urls"

# Template configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# WSGI application for deployment
WSGI_APPLICATION = "dnd_tracker.wsgi.application"

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Use DATABASE_URL for production, individual settings for development
if os.getenv("DATABASE_URL"):
    # Production: Use DATABASE_URL (Neon)
    DATABASES = {
        "default": dj_database_url.config(
            env="DATABASE_URL", conn_max_age=600, ssl_require=True
        )
    }
else:
    # Development: Use individual settings without SSL requirement
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": os.getenv("DB_PORT"),
            "OPTIONS": {},  # No SSL requirement for local development
        }
    }

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

# Password validation rules for user accounts
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

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

# Language and timezone settings
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC FILES CONFIGURATION
# =============================================================================

# Static files (CSS, JavaScript, Images) configuration
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# =============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# =============================================================================

# Default primary key field type for models
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# CUSTOM USER MODEL
# =============================================================================

# Use custom User model with 2FA support
AUTH_USER_MODEL = "accounts.User"

# =============================================================================
# AUTHENTICATION SETTINGS
# =============================================================================

# Login/logout URL configuration
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "campaigns:campaign_list"
LOGOUT_REDIRECT_URL = "accounts:login"

# =============================================================================
# SESSION CONFIGURATION
# =============================================================================

# Session settings for user authentication
SESSION_COOKIE_AGE = 86400  # 24 hours in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_SECURE = not DEBUG  # Use secure cookies in production
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookies

# =============================================================================
# CSRF CONFIGURATION
# =============================================================================

# CSRF protection settings
CSRF_COOKIE_SECURE = not DEBUG  # Use secure cookies in production
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access to CSRF cookies

# =============================================================================
# SECURITY HEADERS CONFIGURATION
# =============================================================================

# Security headers for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# =============================================================================
# CACHE CONFIGURATION
# =============================================================================

# Redis cache configuration for better performance
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "dnd_tracker",
        "TIMEOUT": 300,  # 5 minutes default timeout
    }
}

# =============================================================================
# ADDITIONAL SECURITY SETTINGS
# =============================================================================

# Additional security settings for production
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# Make sure Django knows it's behind Render's proxy and uses HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

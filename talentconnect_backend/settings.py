"""
Django settings for talentconnect_backend project.
"""

from pathlib import Path
import os
import ssl
import certifi  # type: ignore

# ======================
# BASE DIRECTORY
# ======================

BASE_DIR = Path(__file__).resolve().parent.parent

# ======================
# SECURITY
# ======================

SECRET_KEY = 'django-insecure-&^+kxdfr!$xjyq6#$z_gj#fyje9w!#n+hv75+)8u_vl%rz^a-o'

DEBUG = True

ALLOWED_HOSTS = [
    ".vercel.app",
    "127.0.0.1",
    "localhost",
]
CSRF_TRUSTED_ORIGINS = [
    "https://localhost:8000",
    "https://127.0.0.1:8000",
    "https://talentconnect-backend-etqc.vercel.app",
]

# ======================
# LOGIN
# ======================

LOGIN_URL = '/login/'
LOGIN_URL = '/accounts/login/'

# ======================
# INSTALLED APPS
# ======================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',
    'contact',
    'videos',
]

# ======================
# MIDDLEWARE
# ======================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise should be directly after SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ======================
# URLS & WSGI
# ======================

ROOT_URLCONF = 'talentconnect_backend.urls'

WSGI_APPLICATION = 'talentconnect_backend.wsgi.application'

# ======================
# TEMPLATES
# ======================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # Add templates folder here if needed
        'DIRS': [],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ======================
# DATABASE
# ======================
import os
import dj_database_url
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True
    )
}

# ======================
# PASSWORD VALIDATION
# ======================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ======================
# INTERNATIONALIZATION
# ======================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# ======================
# STATIC FILES
# ======================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "videos/static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ======================
# MEDIA FILES
# ======================
import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ======================
# SSL FIX
# ======================

ssl._create_default_https_context = lambda: ssl.create_default_context(
    cafile=certifi.where()
)

# ======================
# EMAIL CONFIGURATION
# ======================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587

EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

EMAIL_HOST_USER = 'abduhamidsuleiman059@gmail.com'
EMAIL_HOST_PASSWORD = 'txum gdxq yuwc wwns'

DEFAULT_FROM_EMAIL = 'abduhamidsuleiman059@gmail.com'
ADMIN_EMAIL = 'abduhamidsuleiman059@gmail.com'

# ======================
# DEFAULT AUTO FIELD
# ======================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' 
"""Clean Django settings (UTF-8, regenerated, no null bytes)"""
from __future__ import annotations
import os
from pathlib import Path
import dj_database_url
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = list(config('DJANGO_ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv()))
# Añadir automáticamente el hostname de Azure App Service si existe
_azure_host = os.environ.get('WEBSITE_HOSTNAME')
if _azure_host and _azure_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_azure_host)
# IPs internas usadas por health probes en App Service (evita DisallowedHost en logs)
for _probe_ip in ('169.254.130.1', '169.254.130.2', '169.254.130.3'):
    if _probe_ip not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_probe_ip)
if DEBUG:
    for host in ('127.0.0.1', 'localhost'):
        if host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'channels',
    'apps.diagrams',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'diagram_backend.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'diagram_backend.wsgi.application'
# ASGI principal (HTTP + WebSockets) definido en asgi.py
ASGI_APPLICATION = 'diagram_backend.asgi.application'
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600
    )
}
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'es-bo'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
############################################
# CORS
############################################
# FRONTEND_ORIGINS= http://localhost:3000,https://tu-dominio.com
_frontend_origins = config('FRONTEND_ORIGINS', default='', cast=str)
if _frontend_origins.strip():
    # Lista explícita
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _frontend_origins.split(',') if o.strip()]
    CORS_ALLOW_ALL_ORIGINS = False
else:
    # Solo permitir todo en modo DEBUG
    CORS_ALLOW_ALL_ORIGINS = DEBUG
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}
############################################
# Channels / WebSockets
############################################
# Toggle explícito: solo activamos Redis si CHANNELS_ENABLE_REDIS=true
CHANNELS_ENABLE_REDIS = config('CHANNELS_ENABLE_REDIS', default=False, cast=bool)
REDIS_URL = config('REDIS_URL', default='') if CHANNELS_ENABLE_REDIS else ''
_redis_fallback_reason = None
if REDIS_URL:
    # Prueba rápida de conectividad sincrónica para decidir si usamos Redis o no.
    try:
        import redis  # paquete sync
        from urllib.parse import urlparse
        parsed = urlparse(REDIS_URL)
        # Opciones de timeout cortas para no bloquear el arranque
        _ssl = parsed.scheme == 'rediss'
        test_client = redis.Redis.from_url(REDIS_URL, socket_connect_timeout=1, socket_timeout=1, ssl=_ssl)
        test_client.ping()
    except Exception as e:  # pragma: no cover - solo en despliegue
        _redis_fallback_reason = str(e)
        REDIS_URL = ''  # forzar fallback a memoria
        print(f"[settings] Redis no disponible, usando InMemoryChannelLayer. Motivo: {_redis_fallback_reason}")

if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
            }
        }
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer'
        }
    }
############################################
# Logging
############################################
LOG_LEVEL = config('LOG_LEVEL', default='INFO').upper()
LOG_SQL = config('LOG_SQL', default=False, cast=bool)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(levelname)s] %(asctime)s %(name)s :: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django.request': {'level': LOG_LEVEL, 'handlers': ['console'], 'propagate': False},
        'channels': {'level': LOG_LEVEL, 'handlers': ['console'], 'propagate': False},
        'django.db.backends': {
            'level': 'DEBUG' if LOG_SQL else 'ERROR',
            'handlers': ['console'],
            'propagate': False
        }
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
if DEBUG:  # pragma: no cover
    print('[settings] Loaded clean UTF-8 settings file | Redis:', 'ON' if REDIS_URL else 'IN-MEMORY')
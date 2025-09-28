"""
Configuración específica para producción con gestión optimizada de conexiones.
Este archivo contiene overrides para producción que minimizan el uso de conexiones DB.
"""
import os
from .settings import *
from decouple import config

# Configuración de base de datos ultra-restrictiva para Azure
if os.getenv('DATABASE_URL'):
    # Configuración específica para evitar agotamiento de conexiones
    DATABASES['default'].update({
        'CONN_MAX_AGE': 0,  # Cerrar inmediatamente
        'CONN_HEALTH_CHECKS': False,  # Desactivar health checks automáticos
        'OPTIONS': {
            'connect_timeout': 3,  # Timeout muy corto
            'keepalives': 0,  # Sin keepalives
            'sslmode': 'require',
        }
    })

# Configuración básica para producción
DEBUG = False  # SIEMPRE False en producción
ALLOWED_HOSTS = ['*']  # Temporal para diagnosticar - cambiar después

# Deshabilitar CSRF temporalmente para diagnóstico
MIDDLEWARE = [m for m in MIDDLEWARE if 'CsrfViewMiddleware' not in m]

# Configuración CORS muy permisiva para diagnóstico
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# REST Framework sin restricciones para diagnóstico
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
}

# Logging para diagnóstico
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.diagrams': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Cache simple
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
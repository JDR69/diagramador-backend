"""
Configuración temporal para diagnóstico - NO usar en producción final
Este archivo desactiva temporalmente algunas validaciones para diagnosticar el error 400
"""
from .settings import *

# Configuración de base de datos ultra-restrictiva para Azure
if os.getenv('DATABASE_URL'):
    DATABASES['default'].update({
        'CONN_MAX_AGE': 0,
        'CONN_HEALTH_CHECKS': False,
        'OPTIONS': {
            'connect_timeout': 3,
            'keepalives': 0,
            'sslmode': 'require',
        }
    })

# Configuración básica
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = [
    'diagram-class-backend-djr-at04hdp0qa6vdk48.brazilsouth-01.azurewebsites.net',
    '*.azurewebsites.net',
    'localhost',
    '127.0.0.1'
]

# TEMPORAL: Deshabilitar CSRF para diagnóstico
MIDDLEWARE = [item for item in MIDDLEWARE if 'CsrfViewMiddleware' not in item]

# Configuración CORS muy permisiva para diagnóstico
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = ['*']

# REST Framework sin autenticación para diagnóstico
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [],  # Sin autenticación
}

# Logging para diagnóstico
LOGGING['loggers']['django']['level'] = 'DEBUG' if DEBUG else 'INFO'
LOGGING['loggers']['apps.diagrams']['level'] = 'DEBUG'
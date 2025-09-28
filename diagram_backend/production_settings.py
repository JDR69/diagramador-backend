"""
Configuración específica para producción con gestión optimizada de conexiones.
Este archivo contiene overr4ides para producción que minimizan el uso de conexiones DB.
"""
import os
from .settings import *

# Configuración de base de datos ultra-restrictiva para Render
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

# Configuración adicional para producción
# En producción, DEBUG DEBE ser False por seguridad
DEBUG = config('DEBUG', default=False, cast=bool)
# Si necesitas debug temporalmente en producción (NO recomendado), 
# configura la variable de entorno DEBUG=True en Azure

# Hosts permitidos específicos para Azure
ALLOWED_HOSTS = [
    'diagram-class-backend-djr-at04hdp0qa6vdk48.brazilsouth-01.azurewebsites.net',
    '*.azurewebsites.net',
    'localhost',
    '127.0.0.1'
]

# Logging optimizado para producción
LOGGING['loggers']['django.db.backends']['level'] = 'ERROR'  # Solo errores críticos
LOGGING['root']['level'] = 'ERROR'

# Configuración de middleware específica para producción
MIDDLEWARE.insert(0, 'apps.diagrams.middleware.ConnectionCleanupMiddleware')

# Configuración de seguridad adicional
SECURE_SSL_REDIRECT = False  # Azure maneja SSL
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Configuración CSRF para producción
CSRF_COOKIE_SECURE = False  # Azure termina SSL
CSRF_COOKIE_HTTPONLY = False  # Permitir acceso desde JavaScript
CSRF_TRUSTED_ORIGINS = [
    'https://diagram-class-backend-djr-at04hdp0qa6vdk48.brazilsouth-01.azurewebsites.net',
    'https://*.azurewebsites.net',
]

# Configuración CORS actualizada para producción
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'https://diagram-class-backend-djr-at04hdp0qa6vdk48.brazilsouth-01.azurewebsites.net',
    'http://localhost:3000',
    'https://localhost:3000',
    'https://*.azurewebsites.net',
]

# Cache para reducir consultas DB
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Sesiones en cache en lugar de DB
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Configuración REST Framework para producción
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}
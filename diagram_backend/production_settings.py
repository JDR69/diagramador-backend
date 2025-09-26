"""
Configuración específica para producción con gestión optimizada de conexiones.
Este archivo contiene overrides para producción que minimizan el uso de conexiones DB.
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
DEBUG = False
ALLOWED_HOSTS = ['*']  # Configurar según tu dominio

# Logging optimizado para producción
LOGGING['loggers']['django.db.backends']['level'] = 'ERROR'  # Solo errores críticos
LOGGING['root']['level'] = 'ERROR'

# Configuración de middleware específica para producción
MIDDLEWARE.insert(0, 'apps.diagrams.middleware.ConnectionCleanupMiddleware')

# Configuración de seguridad adicional
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

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
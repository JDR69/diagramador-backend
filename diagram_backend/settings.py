
"""
Configuración de Django para el proyecto diagram_backend.
"""

import os
from pathlib import Path
from decouple import config
import dj_database_url

# Construye rutas dentro del proyecto como: BASE_DIR / 'subcarpeta'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ADVERTENCIA DE SEGURIDAD: mantén la clave secreta en producción en privado.
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# ADVERTENCIA DE SEGURIDAD: no ejecutes con debug activado en producción.
DEBUG = True  # TEMPORAL para diagnóstico - cambiar a False después

# Configuración de hosts permitidos - funciona tanto para desarrollo como producción
ALLOWED_HOSTS = ['*']  # Temporal para diagnóstico

# Definición de aplicaciones
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    # 'channels',  # Temporalmente deshabilitado
]

LOCAL_APPS = [
    'apps.diagrams',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',  # Temporalmente deshabilitado
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'diagram_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
# ASGI_APPLICATION = 'diagram_backend.asgi.application'  # Temporalmente deshabilitado

# Base de datos
# Configuración que funciona tanto para desarrollo local como Azure
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    # Configuración para Azure/Producción
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=0)
    }
    # Configuración optimizada para Azure
    DATABASES['default'].update({
        'CONN_MAX_AGE': 0,  # Cerrar conexiones inmediatamente
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'connect_timeout': 5,
            'keepalives': 0,
            'sslmode': 'require' if 'postgresql' in DATABASE_URL else 'disable',
        }
    })
else:
    # Configuración para desarrollo local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('POSTGRES_DB', default='diagramdb'),
            'USER': config('POSTGRES_USER', default='diagramuser'),
            'PASSWORD': config('POSTGRES_PASSWORD', default='diagramsecret'),
            'HOST': config('POSTGRES_HOST', default='localhost'),
            'PORT': config('POSTGRES_PORT', default='5432'),
            'CONN_MAX_AGE': 0,
            'CONN_HEALTH_CHECKS': True,
            'OPTIONS': {
                'sslmode': 'require',
                'connect_timeout': 5,
                'keepalives': 0,
            },
        }
    }

# Configuración adicional para gestión de conexiones
DATABASES['default'].setdefault('TEST', {})
DATABASES['default']['TEST']['SERIALIZE'] = False

# Cerrar conexiones automáticamente después de cada request
DATABASE_CONN_MAX_AGE = 0

# Validación de contraseñas
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

# Internacionalización
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Archivos estáticos (CSS, JavaScript, Imágenes)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Tipo de campo de clave primaria por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Configuración de CORS - muy permisiva para diagnóstico
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Configuración de Channels simplificada (temporalmente deshabilitada)
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels.layers.InMemoryChannelLayer'
#     },
# }

# Configuración de Celery (opcional por ahora)
# CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
# CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')

# Configuración de integración de IA (opcional)
# GROQ_API_KEY = config('GROQ_API_KEY', default='')

# Logging simplificado
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

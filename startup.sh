#!/bin/bash

# Script de inicio para Azure App Service
echo "Iniciando aplicación Django en Azure..."

# Ejecutar migraciones
python manage.py migrate --noinput

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Iniciar aplicación con Gunicorn
exec gunicorn diagram_backend.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --max-requests 100 \
    --max-requests-jitter 10 \
    --preload \
    --access-logfile - \
    --error-logfile -
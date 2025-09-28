#!/bin/bash

echo "=== Iniciando aplicación Django en Azure ==="

# Mostrar información del sistema
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Python path: $(which python)"

# Mostrar variables de entorno importantes (sin mostrar secrets)
echo "DEBUG: $DEBUG"
echo "ALLOWED_HOSTS: $DJANGO_ALLOWED_HOSTS"

# Instalar dependencias si es necesario
echo "=== Instalando dependencias ==="
pip install -r requirements.txt

# Ejecutar migraciones
echo "=== Ejecutando migraciones ==="
python manage.py migrate --noinput

# Recolectar archivos estáticos
echo "=== Recolectando archivos estáticos ==="
python manage.py collectstatic --noinput --clear

# Verificar que la aplicación puede arrancar
echo "=== Verificando configuración ==="
python manage.py check --deploy

echo "=== Iniciando servidor Gunicorn ==="
# Asegurarse de que la variable PORT esté definida (Azure Web Apps la define automáticamente)
PORT="${PORT:-8000}"
echo "Puerto utilizado: $PORT"

# Iniciar con Gunicorn para mayor estabilidad en producción
exec gunicorn diagram_backend.wsgi:application \
    --bind=0.0.0.0:$PORT \
    --workers=2 \
    --threads=4 \
    --timeout=120 \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=info
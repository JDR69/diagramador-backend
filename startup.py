import os
import sys
import time

# Configurar variables de entorno para el startup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diagram_backend.settings')

print("=== Iniciando aplicación Django en Azure ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.executable}")

# Verificar variables de entorno críticas
print(f"DEBUG: {os.environ.get('DEBUG', 'Not set')}")
print(f"DJANGO_ALLOWED_HOSTS: {os.environ.get('DJANGO_ALLOWED_HOSTS', 'Not set')}")
print(f"DATABASE_URL: {'Set' if os.environ.get('DATABASE_URL') else 'Not set'}")
print(f"REDIS_URL: {'Set' if os.environ.get('REDIS_URL') else 'Not set'}")

# Importar Django y verificar configuración
import django
print(f"Django version: {django.__version__}")

# Configurar aplicación Django
django.setup()

# Importar funcionalidades de Django
from django.core.management import call_command

# Ejecutar migraciones
print("=== Ejecutando migraciones ===")
call_command('migrate', '--noinput')

# Recolectar archivos estáticos
print("=== Recolectando archivos estáticos ===")
call_command('collectstatic', '--noinput', '--clear')

# Verificar que la aplicación puede arrancar
print("=== Verificando configuración ===")
call_command('check', '--deploy')

print("=== Configuración completada ===")

# Obtener el puerto de la variable de entorno
port = os.environ.get('PORT', '8000')
print(f"=== Iniciando servidor Daphne en puerto {port} ===")

# Iniciar Daphne para WebSockets
import subprocess
subprocess.run([
    sys.executable, '-m', 'daphne',
    '-b', '0.0.0.0',
    '-p', port,
    'diagram_backend.asgi:application',
    '--verbosity', '2'
])
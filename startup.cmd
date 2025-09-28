@echo off
:: Configuración para Azure App Service (Windows)
:: Este archivo le dice a Azure cómo ejecutar la aplicación

echo === Iniciando aplicación Django en Azure (Windows) ===

:: Mostrar información del entorno
echo Python version:
python --version
echo Working directory: %cd%

:: Instalar dependencias
echo === Instalando dependencias ===
pip install -r requirements.txt

:: Ejecutar migraciones
echo === Ejecutando migraciones ===
python manage.py migrate --noinput

:: Recolectar archivos estáticos
echo === Recolectando archivos estáticos ===
python manage.py collectstatic --noinput --clear

:: Verificar configuración
echo === Verificando configuración ===
python manage.py check --deploy

:: El servidor se iniciará automáticamente por el módulo FastCGI
echo === Configuración completada ===
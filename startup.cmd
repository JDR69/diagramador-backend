@echo off
echo === Iniciando aplicación Django en Azure (Windows) ===

echo Python version:
python --version
echo Working directory: %cd%

echo === Instalando dependencias ===
pip install -r requirements.txt

echo === Ejecutando migraciones ===
python manage.py migrate --noinput

echo === Recolectando archivos estáticos ===
python manage.py collectstatic --noinput --clear

echo === Aplicación lista para ejecutar con FastCGI ===
REM No es necesario iniciar explícitamente el servidor, Azure lo hará automáticamente
# Configuración para Azure App Service
# Este archivo le dice a Azure cómo ejecutar la aplicación

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate --noinput

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Iniciar la aplicación
exec daphne -b 0.0.0.0 -p $PORT diagram_backend.asgi:application
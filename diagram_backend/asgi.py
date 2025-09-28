
import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diagram_backend.settings')

# Para resolver el error 503, usamos solo la aplicación HTTP hasta que el problema se resuelva
# Más tarde, podemos volver a agregar el soporte para WebSockets
from django.core.asgi import get_asgi_application
application = get_asgi_application()

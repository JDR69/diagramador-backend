import os
import sys
import django.core.wsgi

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diagram_backend.settings')
application = django.core.wsgi.get_wsgi_application()
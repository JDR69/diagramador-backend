
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def root_view(request):
    return JsonResponse({
        'message': 'Diagram Backend API',
        'status': 'ok',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/app/diagrams/',
            'health': '/api/app/diagrams/health/',
        }
    })

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('api/app/diagrams/', include('apps.diagrams.urls')),
]

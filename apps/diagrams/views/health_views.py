from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Endpoint simple para verificar que la aplicación funciona"""
    return JsonResponse({
        'status': 'ok',
        'message': 'API funcionando correctamente',
        'timestamp': str(timezone.now())
    })

@csrf_exempt
@require_http_methods(["GET", "POST"])
def test_endpoint(request):
    """Endpoint de prueba para diagnosticar problemas"""
    return JsonResponse({
        'method': request.method,
        'path': request.path,
        'headers': dict(request.headers),
        'status': 'success'
    })
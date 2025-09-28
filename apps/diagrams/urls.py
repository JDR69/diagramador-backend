
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiagramViewSet, ClassEntityViewSet, RelationshipViewSet
from .views.health_views import health_check, test_endpoint

router = DefaultRouter()
router.register(r'diagrams', DiagramViewSet)
router.register(r'classes', ClassEntityViewSet)
router.register(r'relationships', RelationshipViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', health_check, name='health-check'),
    path('test/', test_endpoint, name='test-endpoint'),
]

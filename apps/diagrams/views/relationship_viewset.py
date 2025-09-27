"""
ViewSet para relaciones
"""
from rest_framework import viewsets

from ..models import Relacion
from ..serializers import SerializadorRelacion


class RelationshipViewSet(viewsets.ModelViewSet):
    """Conjunto de vistas para operaciones CRUD de relaciones"""
    queryset = Relacion.objects.all()
    serializer_class = SerializadorRelacion


# Legacy alias
VistaConjuntoRelaciones = RelationshipViewSet
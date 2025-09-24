from rest_framework import viewsets

from ..models import Relacion
from ..serializers import SerializadorRelacion

class VistaConjuntoRelaciones(viewsets.ModelViewSet):
    """Conjunto de vistas para operaciones CRUD de relaciones"""
    queryset = Relacion.objects.all()
    serializer_class = SerializadorRelacion
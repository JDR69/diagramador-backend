"""
Serializador para diagramas
"""
from rest_framework import serializers
from ..models import Diagrama
from .entidad_clase_serializer import SerializadorEntidadClase
from .relacion_serializer import SerializadorRelacion


class SerializadorDiagrama(serializers.ModelSerializer):
    """Serializador para diagramas"""
    classes = SerializadorEntidadClase(many=True, read_only=True)
    relationships = SerializadorRelacion(many=True, read_only=True)
    
    class Meta:
        model = Diagrama
        fields = [
            'id', 'name', 'description', 'classes', 'relationships',
            'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
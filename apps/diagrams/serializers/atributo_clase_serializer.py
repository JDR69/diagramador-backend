"""
Serializador para atributos de clase
"""
from rest_framework import serializers
from ..models import AtributoClase


class SerializadorAtributoClase(serializers.ModelSerializer):
    """Serializador para atributos de clase"""
    
    class Meta:
        model = AtributoClase
        fields = ['id', 'name', 'data_type', 'visibility', 'created_at']
        read_only_fields = ['id', 'created_at']
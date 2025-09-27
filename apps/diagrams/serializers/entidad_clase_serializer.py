"""
Serializador para entidades de clase
"""
from rest_framework import serializers
from ..models import EntidadClase
from .atributo_clase_serializer import SerializadorAtributoClase


class SerializadorEntidadClase(serializers.ModelSerializer):
    """Serializador para entidades de clase"""
    attributes = SerializadorAtributoClase(many=True, read_only=True)
    position = serializers.SerializerMethodField()
    
    class Meta:
        model = EntidadClase
        fields = ['id', 'name', 'position', 'attributes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_position(self, obj):
        return {'x': obj.position_x, 'y': obj.position_y}
    
    def update(self, instance, validated_data):
        # Handle position updates
        if 'position' in self.initial_data:
            position = self.initial_data['position']
            instance.position_x = position.get('x', instance.position_x)
            instance.position_y = position.get('y', instance.position_y)
        
        return super().update(instance, validated_data)
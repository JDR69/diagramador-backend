"""
Serializador para relaciones
"""
from rest_framework import serializers
from ..models import Relacion, EntidadClase


class SerializadorRelacion(serializers.ModelSerializer):
    """Serializador para relaciones"""
    from_class = serializers.PrimaryKeyRelatedField(queryset=EntidadClase.objects.all())
    to_class = serializers.PrimaryKeyRelatedField(queryset=EntidadClase.objects.all())
    cardinality = serializers.SerializerMethodField()

    class Meta:
        model = Relacion
        fields = [
            'id', 'from_class', 'to_class', 'relationship_type',
            'cardinality', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_cardinality(self, obj):
        return {
            'from': obj.cardinality_from,
            'to': obj.cardinality_to
        }
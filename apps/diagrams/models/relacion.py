"""
Modelo de relación entre clases
"""
from django.db import models
import uuid
from .diagrama import Diagrama
from .entidad_clase import EntidadClase


class Relacion(models.Model):
    """Modelo de relación entre clases"""
    RELATIONSHIP_TYPES = [
        ('association', 'Association'),
        ('inheritance', 'Inheritance'),
        ('composition', 'Composition'),
        ('aggregation', 'Aggregation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    diagram = models.ForeignKey(Diagrama, on_delete=models.CASCADE, related_name='relationships')
    from_class = models.ForeignKey(EntidadClase, on_delete=models.CASCADE, related_name='outgoing_relationships')
    to_class = models.ForeignKey(EntidadClase, on_delete=models.CASCADE, related_name='incoming_relationships')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES, default='association')
    cardinality_from = models.CharField(max_length=10, default='1')
    cardinality_to = models.CharField(max_length=10, default='1')
    created_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'relationships'
        unique_together = ['from_class', 'to_class', 'relationship_type']
    
    def __str__(self):
        return f"{self.from_class.name} -> {self.to_class.name} ({self.relationship_type})"
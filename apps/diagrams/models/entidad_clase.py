"""
Modelo de entidad de clase que representa clases UML
"""
from django.db import models
import uuid
from .diagrama import Diagrama


class EntidadClase(models.Model):
    """Modelo de entidad de clase que representa clases UML"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    diagram = models.ForeignKey(Diagrama, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=100)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'class_entities'
        unique_together = ['diagram', 'name']
    
    def __str__(self):
        return f"{self.diagram.name} - {self.name}"
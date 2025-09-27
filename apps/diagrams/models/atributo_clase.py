"""
Modelo de atributo de clase
"""
from django.db import models
import uuid
from .entidad_clase import EntidadClase


class AtributoClase(models.Model):
    """Modelo de atributo de clase"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_entity = models.ForeignKey(EntidadClase, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=50, default='String')
    visibility = models.CharField(
        max_length=10,
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
            ('protected', 'Protected'),
        ],
        default='public'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'class_attributes'
        unique_together = ['class_entity', 'name']
    
    def __str__(self):
        return f"{self.class_entity.name}.{self.name}"
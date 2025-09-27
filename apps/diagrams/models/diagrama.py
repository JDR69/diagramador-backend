"""
Modelos para la gestión de diagramas - Diagrama
"""
from django.db import models
from django.contrib.auth.models import User
import uuid


class Diagrama(models.Model):
    """Modelo de diagrama que representa un diagrama de clases"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default="Nuevo Diagrama")
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'diagrams'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name
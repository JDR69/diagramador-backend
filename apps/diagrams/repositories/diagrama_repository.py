"""
Repositorio para acceso a datos de diagramas
"""
from typing import List, Dict, Any, Optional
from django.db.models import Prefetch
from ..models import Diagrama, EntidadClase


class RepositorioDiagrama:
    """Repositorio para acceso a datos de diagramas"""
    
    def create(self, data: Dict[str, Any]) -> Diagrama:
        """Crear un nuevo diagrama"""
        return Diagrama.objects.create(**data)
    
    def get_by_id(self, diagram_id: str) -> Optional[Diagrama]:
        """Obtener diagrama por ID"""
        try:
            return Diagrama.objects.get(id=diagram_id)
        except Diagrama.DoesNotExist:
            return None
    
    def get_with_details(self, diagram_id: str) -> Optional[Diagrama]:
        """Obtener diagrama con todos los datos relacionados"""
        try:
            return Diagrama.objects.prefetch_related(
                Prefetch('classes', queryset=EntidadClase.objects.prefetch_related('attributes')),
                'relationships__from_class',
                'relationships__to_class'
            ).get(id=diagram_id)
        except Diagrama.DoesNotExist:
            return None
    
    def list_diagrams(self, user=None, is_public=None) -> List[Diagrama]:
        """Listar diagramas con filtrado opcional"""
        queryset = Diagrama.objects.all()
        if user:
            queryset = queryset.filter(created_by=user)
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public)
        return list(queryset)
    
    def update(self, diagram: Diagrama, data: Dict[str, Any]) -> Diagrama:
        """Actualizar diagrama"""
        for field, value in data.items():
            setattr(diagram, field, value)
        diagram.save()
        return diagram
    
    def delete(self, diagram_id: str) -> bool:
        """Eliminar diagrama"""
        try:
            diagram = Diagrama.objects.get(id=diagram_id)
            diagram.delete()
            return True
        except Diagrama.DoesNotExist:
            return False


# Alias en inglés para compatibilidad
DiagramRepository = RepositorioDiagrama
"""
Repositorio para acceso a datos de relaciones
"""
from typing import Dict, Any, Optional
from ..models import Diagrama, EntidadClase, Relacion


class RepositorioRelacion:
    """Repositorio para acceso a datos de relaciones"""
    
    def create(self, diagram: Diagrama, relation_data: Dict[str, Any], class_mapping: Dict[str, EntidadClase]) -> Optional[Relacion]:
        """Crear relación entre clases"""
        from_class_name = relation_data.get('from')
        to_class_name = relation_data.get('to')
        
        if from_class_name not in class_mapping or to_class_name not in class_mapping:
            return None
        
        cardinality = relation_data.get('cardinality', {'from': '1', 'to': '1'})
        
        return Relacion.objects.create(
            diagram=diagram,
            from_class=class_mapping[from_class_name],
            to_class=class_mapping[to_class_name],
            relationship_type=relation_data.get('type', 'association'),
            cardinality_from=cardinality['from'],
            cardinality_to=cardinality['to']
        )
    
    def get_by_id(self, relation_id: str) -> Optional[Relacion]:
        """Obtener relación por ID"""
        try:
            return Relacion.objects.get(id=relation_id)
        except Relacion.DoesNotExist:
            return None
    
    def update(self, relation: Relacion, data: Dict[str, Any]) -> Relacion:
        """Actualizar relación"""
        for field, value in data.items():
            if field == 'cardinality':
                relation.cardinality_from = value.get('from', relation.cardinality_from)
                relation.cardinality_to = value.get('to', relation.cardinality_to)
            else:
                setattr(relation, field, value)
        relation.save()
        return relation
    
    def delete(self, relation_id: str) -> bool:
        """Eliminar relación"""
        try:
            relation = Relacion.objects.get(id=relation_id)
            relation.delete()
            return True
        except Relacion.DoesNotExist:
            return False


# Alias en inglés para compatibilidad
RelationshipRepository = RepositorioRelacion
"""
Repositorio para acceso a datos de entidades de clase
"""
from typing import List, Dict, Any, Optional
from ..models import Diagrama, EntidadClase, AtributoClase


class RepositorioEntidadClase:
    """Repositorio para acceso a datos de entidades de clase"""
    
    def create_with_attributes(self, diagram: Diagrama, class_data: Dict[str, Any]) -> EntidadClase:
        """Crear entidad de clase con atributos"""
        attributes_data = class_data.pop('attributes', [])
        position = class_data.pop('position', {'x': 0, 'y': 0})
        class_entity = EntidadClase.objects.create(
            diagram=diagram,
            position_x=position['x'],
            position_y=position['y'],
            **class_data
        )
        # Crear atributos
        for attr_name in attributes_data:
            AtributoClase.objects.create(
                class_entity=class_entity,
                name=attr_name,
                data_type='String'
            )
        return class_entity
    
    def get_by_id(self, class_id: str) -> Optional[EntidadClase]:
        """Obtener entidad de clase por ID"""
        try:
            return EntidadClase.objects.get(id=class_id)
        except EntidadClase.DoesNotExist:
            return None
    
    def update_class(self, class_entity: EntidadClase, class_data: Dict[str, Any]) -> EntidadClase:
        """Actualizar entidad de clase"""
        # Update basic fields
        for field in ['name']:
            if field in class_data:
                setattr(class_entity, field, class_data[field])
        
        # Update position
        if 'position' in class_data:
            position = class_data['position']
            class_entity.position_x = position['x']
            class_entity.position_y = position['y']
        
        class_entity.save()
        
        # Update attributes
        if 'attributes' in class_data:
            self._update_attributes(class_entity, class_data['attributes'])
        
        return class_entity
    
    def _update_attributes(self, class_entity: EntidadClase, attributes_data: List[str]):
        """Actualizar atributos de clase"""
        existing_attrs = {attr.name: attr for attr in class_entity.attributes.all()}
        new_attr_names = set(attributes_data)
        
        # Remove deleted attributes
        for name, attr in existing_attrs.items():
            if name not in new_attr_names:
                attr.delete()
        
        # Add new attributes
        for attr_name in new_attr_names:
            if attr_name not in existing_attrs:
                AtributoClase.objects.create(
                    class_entity=class_entity,
                    name=attr_name,
                    data_type='String'
                )


# Alias en inglés para compatibilidad
ClassEntityRepository = RepositorioEntidadClase
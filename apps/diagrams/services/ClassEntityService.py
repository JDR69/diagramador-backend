from typing import Dict, Any
from ..models import EntidadClase, AtributoClase
from ..repositories import ClassEntityRepository

class ClassEntityService:
    """Servicio para operaciones de entidades de clase"""
    def __init__(self):
        self.class_repo = ClassEntityRepository()

    def agregar_atributo(self, class_id: str, attribute_data: Dict[str, Any]) -> AtributoClase:
        """Agregar atributo a una clase"""
        class_entity = self.class_repo.get_by_id(class_id)
        return AtributoClase.objects.create(
            class_entity=class_entity,
            **attribute_data
        )

    def eliminar_atributo(self, class_id: str, attribute_name: str) -> bool:
        """Eliminar atributo de una clase"""
        try:
            class_entity = self.class_repo.get_by_id(class_id)
            attribute = class_entity.attributes.get(name=attribute_name)
            attribute.delete()
            return True
        except AtributoClase.DoesNotExist:
            return False

    def actualizar_posicion_clase(self, class_id: str, position: Dict[str, int]) -> EntidadClase:
        """Actualizar posición de la clase"""
        class_entity = self.class_repo.get_by_id(class_id)
        class_entity.position_x = position['x']
        class_entity.position_y = position['y']
        class_entity.save()
        return class_entity
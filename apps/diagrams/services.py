"""
Servicios de lógica de negocio - Capa de Negocio
"""
from typing import List, Dict, Any, Optional
from django.db import transaction
from .models import Diagrama, EntidadClase, AtributoClase, Relacion
from .repositories import DiagramRepository, ClassEntityRepository, RelationshipRepository



class DiagramService:
    """Servicio para la lógica de negocio de diagramas"""
    def __init__(self):
        self.diagram_repo = DiagramRepository()
        self.class_repo = ClassEntityRepository()
        self.relationship_repo = RelationshipRepository()

    def crear_diagrama(self, data: Dict[str, Any]) -> Diagrama:
        """Crear un nuevo diagrama con clases y relaciones"""
        with transaction.atomic():
            diagram = self.diagram_repo.create(data)

            # Process classes
            classes_data = data.get('classes', [])
            class_mapping = {}

            for class_data in classes_data:
                class_entity = self.class_repo.create_with_attributes(
                    diagram=diagram,
                    class_data=class_data
                )
                class_mapping[class_data['name']] = class_entity

            # Process relationships
            relationships_data = data.get('relationships', [])
            for rel_data in relationships_data:
                self.relationship_repo.create_relationship(
                    diagram=diagram,
                    relationship_data=rel_data,
                    class_mapping=class_mapping
                )

            return diagram

    def actualizar_diagrama(self, diagram_id: str, data: Dict[str, Any]) -> Diagrama:
        """Actualizar diagrama con nueva información, incluyendo clases, atributos y relaciones"""
        with transaction.atomic():
            diagram = self.diagram_repo.get_by_id(diagram_id)
            # Actualizar info básica
            for field in ['name', 'description', 'is_public']:
                if field in data:
                    setattr(diagram, field, data[field])
            diagram.save()

            # Actualizar clases y atributos
            if 'classes' in data:
                self._actualizar_clases_y_atributos(diagram, data['classes'])

            # Actualizar relaciones
            if 'relationships' in data:
                self._actualizar_relaciones(diagram, data['relationships'])

            return diagram

    def _actualizar_clases_y_atributos(self, diagram: Diagrama, classes_data: List[Dict]):
        """Actualizar clases y atributos de un diagrama"""
        from .models import EntidadClase, AtributoClase
        # Mapear clases existentes por id y por nombre
        existing_classes = {str(cls.id): cls for cls in diagram.classes.all()}
        existing_classes_by_name = {cls.name: cls for cls in diagram.classes.all()}
        received_ids = set()
        new_class_names = set()

        for class_data in classes_data:
            class_id = str(class_data.get('id', ''))
            class_name = class_data.get('name')
            new_class_names.add(class_name)
            # Si existe por id, actualizar
            if class_id and class_id in existing_classes:
                class_entity = existing_classes[class_id]
                class_entity.name = class_name
                pos = class_data.get('position', {'x': 0, 'y': 0})
                class_entity.position_x = pos.get('x', 0)
                class_entity.position_y = pos.get('y', 0)
                class_entity.save()
                received_ids.add(class_id)
            # Si no existe, crear
            elif class_name and class_name not in existing_classes_by_name:
                pos = class_data.get('position', {'x': 0, 'y': 0})
                class_entity = EntidadClase.objects.create(
                    diagram=diagram,
                    name=class_name,
                    position_x=pos.get('x', 0),
                    position_y=pos.get('y', 0)
                )
                received_ids.add(str(class_entity.id))
            else:
                # Si existe por nombre pero no por id, actualizar
                class_entity = existing_classes_by_name[class_name]
                pos = class_data.get('position', {'x': 0, 'y': 0})
                class_entity.position_x = pos.get('x', 0)
                class_entity.position_y = pos.get('y', 0)
                class_entity.save()
                received_ids.add(str(class_entity.id))

            # Actualizar atributos
            if class_entity:
                attrs = class_data.get('attributes', [])
                # Eliminar atributos que ya no están
                existing_attrs = {attr.name: attr for attr in class_entity.attributes.all()}
                new_attr_names = set(attrs)
                for name, attr in existing_attrs.items():
                    if name not in new_attr_names:
                        attr.delete()
                # Crear nuevos atributos
                for attr_name in new_attr_names:
                    if attr_name not in existing_attrs:
                        AtributoClase.objects.create(
                            class_entity=class_entity,
                            name=attr_name,
                            data_type='String'
                        )

        # Eliminar clases que ya no están
        for cls in diagram.classes.all():
            if str(cls.id) not in received_ids and cls.name not in new_class_names:
                cls.delete()

    def _actualizar_clases(self, diagram: Diagrama, classes_data: List[Dict]):
        """Actualizar clases de un diagrama"""
        existing_classes = {cls.name: cls for cls in diagram.classes.all()}
        new_class_names = {cls_data['name'] for cls_data in classes_data}

        # Remove deleted classes
        for name, class_entity in existing_classes.items():
            if name not in new_class_names:
                class_entity.delete()

        # Update or create classes
        for class_data in classes_data:
            if class_data['name'] in existing_classes:
                self.class_repo.update_class(
                    existing_classes[class_data['name']],
                    class_data
                )
            else:
                self.class_repo.create_with_attributes(diagram, class_data)

    def _actualizar_relaciones(self, diagram: Diagrama, relationships_data: List[Dict]):
        """Actualizar relaciones de un diagrama"""
        from .models import Relacion, EntidadClase
        # Eliminar relaciones existentes
        diagram.relationships.all().delete()

        # Mapear clases por id
        class_mapping = {str(cls.id): cls for cls in diagram.classes.all()}

        for rel_data in relationships_data:
            from_id = str(rel_data.get('from'))
            to_id = str(rel_data.get('to'))
            rel_type = rel_data.get('type', 'association')
            cardinality = rel_data.get('cardinality', {'from': '1', 'to': '1'})
            from_class = class_mapping.get(from_id)
            to_class = class_mapping.get(to_id)
            if from_class and to_class:
                Relacion.objects.create(
                    diagram=diagram,
                    from_class=from_class,
                    to_class=to_class,
                    relationship_type=rel_type,
                    cardinality_from=cardinality.get('from', '1'),
                    cardinality_to=cardinality.get('to', '1')
                )

    def obtener_diagrama_con_detalles(self, diagram_id: str) -> Optional[Diagrama]:
        """Obtener diagrama con todos los datos relacionados"""
        return self.diagram_repo.get_with_details(diagram_id)

    def listar_diagramas(self, user=None, is_public=None) -> List[Diagrama]:
        """Listar diagramas con filtrado opcional"""
        return self.diagram_repo.list_diagrams(user=user, is_public=is_public)

    def eliminar_diagrama(self, diagram_id: str) -> bool:
        """Eliminar un diagrama"""
        return self.diagram_repo.delete(diagram_id)



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

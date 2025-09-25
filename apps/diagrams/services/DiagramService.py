from typing import List, Dict, Any, Optional
from django.db import transaction
from ..models import Diagrama, EntidadClase, AtributoClase, Relacion
from ..repositories import DiagramRepository, ClassEntityRepository, RelationshipRepository

class DiagramService:
    """Servicio para la lógica de negocio de diagramas"""
    def __init__(self):
        self.repositorio_diagrama = DiagramRepository()
        self.repositorio_clase = ClassEntityRepository()
        self.repositorio_relacion = RelationshipRepository()

    def crear_diagrama(self, datos: Dict[str, Any]) -> Diagrama:
        """Crear un nuevo diagrama con clases y relaciones"""
        with transaction.atomic():
            diagrama = self.repositorio_diagrama.create(datos)

            # Procesar clases
            datos_clases = datos.get('classes', [])
            mapeo_clases = {}

            for datos_clase in datos_clases:
                clase = self.repositorio_clase.create_with_attributes(
                    diagram=diagrama,
                    class_data=datos_clase
                )
                mapeo_clases[datos_clase['name']] = clase

            # Procesar relaciones
            datos_relaciones = datos.get('relationships', [])
            for datos_rel in datos_relaciones:
                self.repositorio_relacion.create_relationship(
                    diagram=diagrama,
                    relationship_data=datos_rel,
                    class_mapping=mapeo_clases
                )

            return diagrama

    def actualizar_diagrama(self, diagrama_id: str, datos: Dict[str, Any]) -> Diagrama:
        """Actualizar diagrama con nueva información, incluyendo clases, atributos y relaciones"""
        with transaction.atomic():
            diagrama = self.repositorio_diagrama.get_by_id(diagrama_id)
            # Actualizar info básica
            for campo in ['name', 'description', 'is_public']:
                if campo in datos:
                    setattr(diagrama, campo, datos[campo])
            diagrama.save()

            # Actualizar clases y atributos
            if 'classes' in datos:
                self._actualizar_clases_y_atributos(diagrama, datos['classes'])

            # Actualizar relaciones
            if 'relationships' in datos:
                self._actualizar_relaciones(diagrama, datos['relationships'])

            return diagrama

    def _actualizar_clases_y_atributos(self, diagrama: Diagrama, datos_clases: List[Dict]):
        """Actualizar clases y atributos de un diagrama"""
        existentes_por_id = {str(cls.id): cls for cls in diagrama.classes.all()}
        existentes_por_nombre = {cls.name: cls for cls in diagrama.classes.all()}
        ids_recibidos = set()
        nombres_nuevos = set()

        for datos_clase in datos_clases:
            id_clase = str(datos_clase.get('id', ''))
            nombre_clase = datos_clase.get('name')
            # Asegurarse de que la posición se procesa correctamente
            pos = datos_clase.get('position', {})
            if isinstance(pos, dict) and 'x' in pos and 'y' in pos:
                pos_x = pos.get('x', 0)
                pos_y = pos.get('y', 0)
            else:
                pos_x = 0
                pos_y = 0
                
            nombres_nuevos.add(nombre_clase)
            # Si existe por id, actualizar
            if id_clase and id_clase in existentes_por_id:
                clase = existentes_por_id[id_clase]
                clase.name = nombre_clase
                clase.position_x = pos_x
                clase.position_y = pos_y
                clase.save()
                ids_recibidos.add(id_clase)
            # Si no existe, crear
            elif nombre_clase and nombre_clase not in existentes_por_nombre:
                clase = EntidadClase.objects.create(
                    diagram=diagrama,
                    name=nombre_clase,
                    position_x=pos_x,
                    position_y=pos_y
                )
                ids_recibidos.add(str(clase.id))
            else:
                # Si existe por nombre pero no por id, actualizar
                clase = existentes_por_nombre[nombre_clase]
                clase.position_x = pos_x
                clase.position_y = pos_y
                clase.save()
                ids_recibidos.add(str(clase.id))

            # Actualizar atributos
            if clase:
                atributos = datos_clase.get('attributes', [])
                existentes_atributos = {attr.name: attr for attr in clase.attributes.all()}
                nuevos_nombres = set(atributos)
                # Eliminar atributos que ya no están
                for nombre, attr in existentes_atributos.items():
                    if nombre not in nuevos_nombres:
                        attr.delete()
                # Crear nuevos atributos
                for nombre_attr in nuevos_nombres:
                    if nombre_attr not in existentes_atributos:
                        AtributoClase.objects.create(
                            class_entity=clase,
                            name=nombre_attr,
                            data_type='String'
                        )

        # Eliminar clases que ya no están
        for cls in diagrama.classes.all():
            if str(cls.id) not in ids_recibidos and cls.name not in nombres_nuevos:
                cls.delete()

    def _actualizar_relaciones(self, diagrama: Diagrama, datos_relaciones: List[Dict]):
        """Actualizar relaciones de un diagrama"""
        # Eliminar relaciones existentes
        diagrama.relationships.all().delete()
        
        # Crear mapa de clases por ID y por nombre para poder buscar por cualquiera
        mapeo_clases_id = {str(cls.id): cls for cls in diagrama.classes.all()}
        
        for rel_data in datos_relaciones:
            # Los datos pueden venir con "from"/"to" como ID o como nombre
            desde_id = str(rel_data.get('from', ''))
            hasta_id = str(rel_data.get('to', ''))
            
            # Buscar clases por ID
            desde_clase = mapeo_clases_id.get(desde_id)
            hasta_clase = mapeo_clases_id.get(hasta_id)
            
            # Si no encontramos por ID, podrían ser referencias por nombre
            if not (desde_clase and hasta_clase) and 'name' in rel_data:
                # Intentar buscar por nombre
                desde_nombre = rel_data.get('fromName', '')
                hasta_nombre = rel_data.get('toName', '')
                mapeo_nombre = {cls.name: cls for cls in diagrama.classes.all()}
                
                desde_clase = desde_clase or mapeo_nombre.get(desde_nombre)
                hasta_clase = hasta_clase or mapeo_nombre.get(hasta_nombre)
            
            if desde_clase and hasta_clase:
                tipo = rel_data.get('type', 'association')
                cardinalidad = rel_data.get('cardinality', {'from': '1', 'to': '1'})
                
                # Debuggear
                print(f"Creando relación: {desde_clase.name} -> {hasta_clase.name}, tipo: {tipo}")
                
                Relacion.objects.create(
                    diagram=diagrama,
                    from_class=desde_clase,
                    to_class=hasta_clase,
                    relationship_type=tipo,
                    cardinality_from=cardinalidad.get('from', '1'),
                    cardinality_to=cardinalidad.get('to', '1')
                )

    def obtener_diagrama_con_detalles(self, diagrama_id: str) -> Optional[Diagrama]:
        """Obtener diagrama con todos los datos relacionados"""
        diagrama = self.repositorio_diagrama.get_with_details(diagrama_id)
        # Debugear las relaciones
        if diagrama:
            print(f"Relaciones: {list(diagrama.relationships.all())}")
        return diagrama

    def listar_diagramas(self, usuario=None, es_publico=None) -> List[Diagrama]:
        """Listar diagramas con filtrado opcional"""
        return self.repositorio_diagrama.list_diagrams(user=usuario, is_public=es_publico)

    def eliminar_diagrama(self, diagrama_id: str) -> bool:
        """Eliminar un diagrama"""
        return self.repositorio_diagrama.delete(diagrama_id)
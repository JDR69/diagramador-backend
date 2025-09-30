from typing import List, Dict, Any, Optional
import logging
from django.db import transaction
from ..models import Diagrama, EntidadClase, AtributoClase, Relacion
from ..repositories import DiagramRepository, ClassEntityRepository, RelationshipRepository

logger = logging.getLogger(__name__)


class ServicioDiagrama:
    """Servicio para la lógica de negocio de diagramas"""
    def __init__(self):
        self.repositorio_diagrama = DiagramRepository()
        self.repositorio_clase = ClassEntityRepository()
        self.repositorio_relacion = RelationshipRepository()

    def crear_diagrama(self, datos: Dict[str, Any]) -> Diagrama:
        """Crear un nuevo diagrama con clases y relaciones"""
        try:
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
                    self.repositorio_relacion.create(
                        diagram=diagrama,
                        relation_data=datos_rel,
                        class_mapping=mapeo_clases
                    )

                return diagrama
        finally:
            pass

    def actualizar_diagrama(self, diagrama_id: str, datos: Dict[str, Any]) -> Diagrama:
        """Actualizar diagrama con nueva información, incluyendo clases, atributos y relaciones"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            with transaction.atomic():
                diagrama = self.repositorio_diagrama.get_by_id(diagrama_id)
                if not diagrama:
                    raise ValueError(f"Diagrama con ID {diagrama_id} no encontrado")
                
                logger.debug(f"[diagrama.actualizar] id={diagrama_id}")
                
                # Actualizar info básica solo si está presente
                for campo in ['name', 'description', 'is_public']:
                    if campo in datos:
                        setattr(diagrama, campo, datos[campo])
                        logger.debug(f"[diagrama.actualizar] campo {campo}")
                
                diagrama.save()

                # Actualizar clases y atributos solo si están en los datos
                if 'classes' in datos and datos['classes']:
                    logger.debug(f"[diagrama.actualizar] clases={len(datos['classes'])}")
                    self._actualizar_clases_y_atributos(diagrama, datos['classes'])

                # Actualizar relaciones solo si están en los datos
                if 'relationships' in datos and datos['relationships']:
                    logger.debug(f"[diagrama.actualizar] relaciones={len(datos['relationships'])}")
                    self._actualizar_relaciones(diagrama, datos['relationships'])

                logger.debug(f"[diagrama.actualizar] ok id={diagrama_id}")
                return diagrama
                
        except Exception as e:
            logger.error(f"Error actualizando diagrama {diagrama_id}: {str(e)}", exc_info=True)
            raise
        finally:
            pass

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
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Solo eliminar relaciones si hay nuevas relaciones para crear
            if datos_relaciones:
                logger.debug(f"[diagrama.relaciones] limpiar={diagrama.relationships.count()}")
                diagrama.relationships.all().delete()

                # Crear mapeo de clases
                mapeo_clases_id = {str(cls.id): cls for cls in diagrama.classes.all()}
                logger.debug(f"[diagrama.relaciones] clases={len(mapeo_clases_id)}")

                relaciones_creadas = 0
                for i, rel_data in enumerate(datos_relaciones):
                    try:
                        logger.debug(f"[diagrama.relaciones] procesando {i}")
                        
                        # Obtener IDs de forma más robusta
                        desde_id = str(rel_data.get('from', '')).strip()
                        hasta_id = str(rel_data.get('to', '')).strip()
                        
                        if not desde_id or not hasta_id:
                            logger.warning(f"IDs inválidos en relación {i}: from={desde_id}, to={hasta_id}")
                            continue
                        
                        # Buscar clases
                        desde_clase = mapeo_clases_id.get(desde_id)
                        hasta_clase = mapeo_clases_id.get(hasta_id)
                        
                        if not desde_clase:
                            logger.warning(f"Clase 'from' no encontrada: {desde_id}")
                            continue
                            
                        if not hasta_clase:
                            logger.warning(f"Clase 'to' no encontrada: {hasta_id}")
                            continue
                        
                        # Crear relación
                        tipo = rel_data.get('type', 'association')
                        cardinalidad = rel_data.get('cardinality', {'from': '1', 'to': '1'})
                        
                        relacion = Relacion.objects.create(
                            diagram=diagrama,
                            from_class=desde_clase,
                            to_class=hasta_clase,
                            relationship_type=tipo,
                            cardinality_from=cardinalidad.get('from', '1'),
                            cardinality_to=cardinalidad.get('to', '1')
                        )
                        relaciones_creadas += 1
                        logger.debug(f"[diagrama.relaciones] creada id={relacion.id}")
                        
                    except Exception as e:
                        logger.error(f"Error procesando relación {i}: {str(e)}")
                        continue
                
                logger.debug(f"[diagrama.relaciones] creadas={relaciones_creadas}/{len(datos_relaciones)}")
            else:
                logger.debug("[diagrama.relaciones] sin cambios")
                
        except Exception as e:
            logger.error(f"Error actualizando relaciones: {str(e)}", exc_info=True)
            raise

    def obtener_diagrama_con_detalles(self, diagrama_id: str) -> Optional[Diagrama]:
        """Obtener diagrama con todos los datos relacionados"""
        diagrama = self.repositorio_diagrama.get_with_details(diagrama_id)
        if diagrama:
            logger.debug(f"[diagram.service] relaciones_count={diagrama.relationships.count()} id={diagrama_id}")
        return diagrama

    def listar_diagramas(self, usuario=None, es_publico=None) -> List[Diagrama]:
        """Listar diagramas con filtrado opcional"""
        return self.repositorio_diagrama.list_diagrams(user=usuario, is_public=es_publico)

    def eliminar_diagrama(self, diagrama_id: str) -> bool:
        """Eliminar un diagrama"""
        return self.repositorio_diagrama.delete(diagrama_id)


# Alias en inglés para compatibilidad
DiagramService = ServicioDiagrama
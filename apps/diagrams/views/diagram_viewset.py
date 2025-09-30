"""
ViewSet para diagramas
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
import logging
import os

from ..models import Diagrama, EntidadClase
from ..serializers import SerializadorDiagrama, SerializadorCrearDiagrama
from ..services import ServicioDiagrama

logger = logging.getLogger(__name__)




class DiagramViewSet(viewsets.ModelViewSet):
    """Conjunto de vistas para operaciones CRUD de diagramas"""
    # Queryset base; se optimiza en get_queryset con prefetch
    queryset = Diagrama.objects.all()
    serializer_class = SerializadorDiagrama
    servicio = ServicioDiagrama()

    def get_queryset(self):
        """Optimiza las consultas al recuperar diagramas para reducir la latencia en refresh.

        Prefetch de:
          - classes + attributes
          - relationships y sus from/to (select_related)
        """
        return (Diagrama.objects
                .prefetch_related('classes__attributes')
                .prefetch_related('relationships__from_class', 'relationships__to_class'))

    def get_serializer_class(self):
        if self.action == 'create':
            return SerializadorCrearDiagrama
        return SerializadorDiagrama

    def create(self, request):
        """Crear un nuevo diagrama"""
        try:
            import time
            from django.db import connection
            t0 = time.perf_counter()
            logger.info(f"[diagrama.crear] inicio campos={list(request.data.keys())}")
            
            serializador = self.get_serializer(data=request.data)
            serializador.is_valid(raise_exception=True)
            
            diagrama = self.servicio.crear_diagrama(serializador.validated_data)
            serializador_respuesta = SerializadorDiagrama(diagrama)
            dt = (time.perf_counter() - t0) * 1000
            logger.info(f"[diagrama.crear] ok id={diagrama.id} ms={dt:.1f}")
            connection.close()
            return Response(serializador_respuesta.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            from django.db import connection
            connection.close()
            logger.error(f"Error en create: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """Obtener diagrama con detalles"""
        try:
            import time
            from django.db import connection
            t0 = time.perf_counter()
            logger.debug(f"[diagrama.obtener] id={pk}")
            
            diagrama = self.servicio.obtener_diagrama_con_detalles(pk)
            if not diagrama:
                connection.close()
                return Response(
                    {'error': 'Diagrama no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializador = SerializadorDiagrama(diagrama)
            dt = (time.perf_counter() - t0) * 1000
            logger.debug(f"[diagrama.obtener] ok id={pk} ms={dt:.1f}")
            connection.close()
            return Response(serializador.data)
            
        except Exception as e:
            from django.db import connection
            connection.close()
            logger.error(f"Error en retrieve: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None, partial=False):
        """Actualizar diagrama"""
        try:
            from django.db import connection
            logger.debug(f"[diagrama.patch] datos recibidos")
            
            # Obtener instancia de forma más segura
            try:
                instance = self.get_object()
            except Exception as e:
                logger.error(f"Error obteniendo objeto: {str(e)}")
                connection.close()
                return Response(
                    {'error': 'Diagrama no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Actualización directa usando el servicio, evitando el serializer
            try:
                diagrama = self.servicio.actualizar_diagrama(pk, request.data)
                serializador_respuesta = self.get_serializer(diagrama)
                return Response(serializador_respuesta.data)
            except Exception as e:
                logger.error(f"Error en servicio: {str(e)}", exc_info=True)
                return Response(
                    {'error': f'Error interno: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error general en update: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """Eliminar diagrama"""
        try:
            exito = self.servicio.eliminar_diagrama(pk)
            if exito:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Diagrama no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        finally:
            pass

    @action(detail=False, methods=['get'])
    def health_check(self, request):
        """Verificar estado del servidor y base de datos"""
        try:
            from django.db import connections
            
            # Verificar conexión a base de datos
            db_status = {}
            for alias in connections:
                try:
                    connection = connections[alias]
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                        db_status[alias] = "OK"
                except Exception as e:
                    db_status[alias] = f"ERROR: {str(e)}"
                finally:
                    if connection.connection is not None:
                        connection.close()
            
            # Información básica del sistema
            info = {
                'status': 'OK',
                'timestamp': timezone.now().isoformat(),
                'database': db_status,
                'django': {
                    'debug': settings.DEBUG,
                    'database_url_configured': bool(os.getenv('DATABASE_URL')),
                    'connections_available': len([s for s in db_status.values() if s == "OK"])
                }
            }
            
            return Response(info)
            
        except Exception as e:
            logger.error(f"Error en health check: {str(e)}", exc_info=True)
            return Response({
                'status': 'ERROR',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            pass

    @action(detail=True, methods=['post'])
    def duplicar(self, request, pk=None):
        """Duplicar un diagrama"""
        original = get_object_or_404(Diagrama, pk=pk)

        # Crear datos duplicados
        datos_duplicado = {
            'name': f"{original.name} (Copia)",
            'description': original.description,
            'is_public': False,
            'classes': [],
            'relationships': []
        }

        # Copiar clases
        for clase in original.classes.all():
            datos_clase = {
                'name': clase.name,
                'position': {'x': clase.position_x, 'y': clase.position_y},
                'attributes': [attr.name for attr in clase.attributes.all()]
            }
            datos_duplicado['classes'].append(datos_clase)

        # Copiar relaciones
        for relacion in original.relationships.all():
            datos_rel = {
                'from': relacion.from_class.name,
                'to': relacion.to_class.name,
                'type': relacion.relationship_type,
                'cardinality': {
                    'from': relacion.cardinality_from,
                    'to': relacion.cardinality_to
                }
            }
            datos_duplicado['relationships'].append(datos_rel)

        # Crear duplicado
        duplicado = self.servicio.crear_diagrama(datos_duplicado)
        serializador = SerializadorDiagrama(duplicado)
        return Response(serializador.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def debug(self, request, pk=None):
        """Endpoint de depuración para ver el estado actual del diagrama"""
        diagrama = self.get_object()
        data = {
            'id': diagrama.id,
            'name': diagrama.name,
            'classes': [
                {
                    'id': cls.id,
                    'name': cls.name,
                    'position': {'x': cls.position_x, 'y': cls.position_y},
                    'attributes': [attr.name for attr in cls.attributes.all()]
                }
                for cls in diagrama.classes.all()
            ],
            'relationships': [
                {
                    'id': rel.id,
                    'from_id': rel.from_class.id,
                    'to_id': rel.to_class.id,
                    'from_name': rel.from_class.name,
                    'to_name': rel.to_class.name,
                    'type': rel.relationship_type,
                    'cardinality': {
                        'from': rel.cardinality_from,
                        'to': rel.cardinality_to
                    }
                }
                for rel in diagrama.relationships.all()
            ]
        }
        return Response(data)

    @action(detail=True, methods=['get'])
    def debug_relationships(self, request, pk=None):
        """Ver solo las relaciones de un diagrama"""
        diagrama = self.get_object()
        relations = [
            {
                'id': str(rel.id),
                'from_id': str(rel.from_class.id), 
                'to_id': str(rel.to_class.id),
                'from_name': rel.from_class.name,
                'to_name': rel.to_class.name,
                'type': rel.relationship_type,
                'cardinality': {
                    'from': rel.cardinality_from,
                    'to': rel.cardinality_to
                }
            }
            for rel in diagrama.relationships.all()
        ]
        
        classes = {str(cls.id): cls.name for cls in diagrama.classes.all()}
        
        return Response({
            'diagram_id': str(diagrama.id),
            'diagram_name': diagrama.name,
            'relations_count': len(relations), 
            'relations': relations,
            'classes': classes
        })

    @action(detail=True, methods=['get'])
    def debug_state(self, request, pk=None):
        """Ver estado completo del diagrama"""
        diagrama = self.get_object()
        
        classes_data = []
        for cls in diagrama.classes.all():
            classes_data.append({
                'id': str(cls.id),
                'name': cls.name,
                'position': {'x': cls.position_x, 'y': cls.position_y},
                'attributes': [attr.name for attr in cls.attributes.all()]
            })
        
        relations_data = []
        for rel in diagrama.relationships.all():
            relations_data.append({
                'id': str(rel.id),
                'from': str(rel.from_class.id),
                'to': str(rel.to_class.id),
                'from_name': rel.from_class.name,
                'to_name': rel.to_class.name,
                'type': rel.relationship_type,
                'cardinality': {
                    'from': rel.cardinality_from,
                    'to': rel.cardinality_to
                }
            })
        
        return Response({
            'diagram_id': str(diagrama.id),
            'diagram_name': diagrama.name,
            'classes_count': len(classes_data),
            'relations_count': len(relations_data),
            'classes': classes_data,
            'relationships': relations_data
        })

    @action(detail=True, methods=['patch'], url_path='positions')
    def actualizar_posiciones(self, request, pk=None):
        """Actualizar posiciones de múltiples clases en un solo request.

        """
        diagrama = self.get_object()
        classes_payload = request.data.get('classes', [])
        if not isinstance(classes_payload, list):
            return Response({'error': 'Formato inválido: classes debe ser lista'}, status=status.HTTP_400_BAD_REQUEST)

        # Mapear datos entrantes
        updates = {}
        for item in classes_payload:
            cid = item.get('id')
            pos = (item.get('position') or {}) if isinstance(item, dict) else {}
            if cid and isinstance(pos, dict) and 'x' in pos and 'y' in pos:
                updates[cid] = pos

        if not updates:
            return Response({'updated': 0, 'classes': []})

        # Cargar solo las clases necesarias pertenecientes al diagrama
        clases = EntidadClase.objects.filter(diagram=diagrama, id__in=list(updates.keys()))
        modificadas = []
        for cls in clases:
            new_pos = updates.get(str(cls.id)) or updates.get(cls.id)
            if new_pos:
                changed = (cls.position_x != new_pos['x']) or (cls.position_y != new_pos['y'])
                cls.position_x = new_pos['x']
                cls.position_y = new_pos['y']
                if changed:
                    cls.save(update_fields=['position_x', 'position_y', 'updated_at'])
                modificadas.append({
                    'id': str(cls.id),
                    'position': {'x': cls.position_x, 'y': cls.position_y}
                })

        return Response({'updated': len(modificadas), 'classes': modificadas})


# Legacy alias
VistaConjuntoDiagramas = DiagramViewSet
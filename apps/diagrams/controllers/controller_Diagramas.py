from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import connections
from django.utils import timezone
from django.conf import settings
import logging
import os

from ..models import Diagrama
from ..serializers import SerializadorDiagrama, SerializadorCrearDiagrama
from ..services.DiagramService import ServicioDiagrama

logger = logging.getLogger(__name__)

def cerrar_conexiones():
    """Utilidad para cerrar todas las conexiones de base de datos."""
    try:
        for alias in connections:
            connection = connections[alias]
            if connection.connection is not None:
                connection.close()
                logger.debug(f"Conexión '{alias}' cerrada")
    except Exception as e:
        logger.error(f"Error cerrando conexiones: {e}")

class VistaConjuntoDiagramas(viewsets.ModelViewSet):
    """Conjunto de vistas para operaciones CRUD de diagramas"""
    queryset = Diagrama.objects.all()
    serializer_class = SerializadorDiagrama
    servicio = ServicioDiagrama()

    def get_serializer_class(self):
        if self.action == 'create':
            return SerializadorCrearDiagrama
        return SerializadorDiagrama

    def create(self, request):
        """Crear un nuevo diagrama"""
        try:
            from django.db import connection
            logger.info(f"Creando diagrama: {request.data}")
            
            serializador = self.get_serializer(data=request.data)
            serializador.is_valid(raise_exception=True)
            
            diagrama = self.servicio.crear_diagrama(serializador.validated_data)
            serializador_respuesta = SerializadorDiagrama(diagrama)
            
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
            from django.db import connection
            logger.info(f"Obteniendo diagrama: {pk}")
            
            diagrama = self.servicio.obtener_diagrama_con_detalles(pk)
            if not diagrama:
                connection.close()
                return Response(
                    {'error': 'Diagrama no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializador = SerializadorDiagrama(diagrama)
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
            logger.info(f"DATOS RECIBIDOS EN PATCH: {request.data}")
            
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
                cerrar_conexiones()
                return Response(serializador_respuesta.data)
            except Exception as e:
                logger.error(f"Error en servicio: {str(e)}", exc_info=True)
                cerrar_conexiones()
                return Response(
                    {'error': f'Error interno: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            cerrar_conexiones()
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
            cerrar_conexiones()

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
            cerrar_conexiones()

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

    @action(detail=False, methods=['get'])
    def health_check(self, request):
        """Verificar el estado del servidor"""
        try:
            from django.db import connection
            from django.utils import timezone
            # Hacer una consulta simple para verificar la conexión a la BD
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            
            connection.close()
            return Response({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            from django.db import connection
            from django.utils import timezone
            connection.close()
            return Response({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }, status=500)

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
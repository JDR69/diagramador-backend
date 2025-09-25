from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import logging

from ..models import Diagrama
from ..serializers import SerializadorDiagrama, SerializadorCrearDiagrama
from ..services.DiagramService import ServicioDiagrama

logger = logging.getLogger(__name__)

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
        serializador = self.get_serializer(data=request.data)
        serializador.is_valid(raise_exception=True)
        diagrama = self.servicio.crear_diagrama(serializador.validated_data)
        serializador_respuesta = SerializadorDiagrama(diagrama)
        return Response(serializador_respuesta.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Obtener diagrama con detalles"""
        diagrama = self.servicio.obtener_diagrama_con_detalles(pk)
        if not diagrama:
            return Response(
                {'error': 'Diagrama no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializador = SerializadorDiagrama(diagrama)
        return Response(serializador.data)

    def update(self, request, pk=None, partial=False):
        """Actualizar diagrama"""
        try:
            logger.info(f"DATOS RECIBIDOS EN PATCH: {request.data}")
            instance = self.get_object()
            serializador = self.get_serializer(instance, data=request.data, partial=partial)
            serializador.is_valid(raise_exception=True)
            diagrama = serializador.save()
            serializador_respuesta = self.get_serializer(diagrama)
            return Response(serializador_respuesta.data)
        except Exception as e:
            logger.error(f"Error en update: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error procesando la solicitud: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """Eliminar diagrama"""
        exito = self.servicio.eliminar_diagrama(pk)
        if exito:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Diagrama no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

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
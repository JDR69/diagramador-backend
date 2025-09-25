from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import Diagrama
from ..serializers import SerializadorDiagrama, SerializadorCrearDiagrama
from ..services.DiagramService import DiagramService

class VistaConjuntoDiagramas(viewsets.ModelViewSet):
    """Conjunto de vistas para operaciones CRUD de diagramas"""
    queryset = Diagrama.objects.all()
    serializer_class = SerializadorDiagrama
    servicio = DiagramService()

    def get_serializer_class(self):
        if self.action == 'create':
            return SerializadorCrearDiagrama
        return SerializadorDiagrama

    def create(self, request):
        """Crear un nuevo diagrama"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        diagrama = self.servicio.crear_diagrama(serializer.validated_data)
        response_serializer = SerializadorDiagrama(diagrama)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Obtener diagrama con detalles"""
        diagrama = self.servicio.obtener_diagrama_con_detalles(pk)
        if not diagrama:
            return Response(
                {'error': 'Diagrama no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = SerializadorDiagrama(diagrama)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Actualizar diagrama"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        diagrama = self.servicio.actualizar_diagrama(pk, serializer.validated_data)
        response_serializer = SerializadorDiagrama(diagrama)
        return Response(response_serializer.data)

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
        serializer = SerializadorDiagrama(duplicado)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import Diagrama
from ..serializers import SerializadorDiagrama, SerializadorCrearDiagrama
from ..services import DiagramService

class VistaConjuntoDiagramas(viewsets.ModelViewSet):
    """Conjunto de vistas para operaciones CRUD de diagramas"""
    queryset = Diagrama.objects.all()
    serializer_class = SerializadorDiagrama
    service = DiagramService()

    def get_serializer_class(self):
        if self.action == 'create':
            return SerializadorCrearDiagrama
        return SerializadorDiagrama

    def create(self, request):
        """Crear un nuevo diagrama"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        diagrama = self.service.create_diagram(serializer.validated_data)
        response_serializer = SerializadorDiagrama(diagrama)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Obtener diagrama con detalles"""
        diagrama = self.service.get_diagram_with_details(pk)
        if not diagrama:
            return Response(
                {'error': 'Diagram not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = SerializadorDiagrama(diagrama)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Actualizar diagrama"""
        diagrama = self.service.update_diagram(pk, request.data)
        serializer = SerializadorDiagrama(diagrama)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """Eliminar diagrama"""
        success = self.service.delete_diagram(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Diagram not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=['post'])
    def duplicar(self, request, pk=None):
        """Duplicar un diagrama"""
        original = get_object_or_404(Diagrama, pk=pk)

        # Crear datos duplicados
        duplicate_data = {
            'name': f"{original.name} (Copia)",
            'description': original.description,
            'is_public': False,
            'classes': [],
            'relationships': []
        }

        # Copiar clases
        for class_entity in original.classes.all():
            class_data = {
                'name': class_entity.name,
                'position': {'x': class_entity.position_x, 'y': class_entity.position_y},
                'attributes': [attr.name for attr in class_entity.attributes.all()]
            }
            duplicate_data['classes'].append(class_data)

        # Copiar relaciones
        for relationship in original.relationships.all():
            rel_data = {
                'from': relationship.from_class.name,
                'to': relationship.to_class.name,
                'type': relationship.relationship_type,
                'cardinality': {
                    'from': relationship.cardinality_from,
                    'to': relationship.cardinality_to
                }
            }
            duplicate_data['relationships'].append(rel_data)

        # Crear duplicado
        duplicate = self.service.create_diagram(duplicate_data)
        serializer = SerializadorDiagrama(duplicate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
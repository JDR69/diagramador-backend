from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import EntidadClase
from ..serializers import SerializadorEntidadClase, SerializadorAtributoClase
from ..services import ClassEntityService

class VistaConjuntoEntidadesClase(viewsets.ModelViewSet):
    """Conjunto de vistas para operaciones CRUD de entidades de clase"""
    queryset = EntidadClase.objects.all()
    serializer_class = SerializadorEntidadClase
    service = ClassEntityService()

    @action(detail=True, methods=['post'])
    def agregar_atributo(self, request, pk=None):
        """Agregar atributo a la clase"""
        attribute = self.service.add_attribute(pk, request.data)
        serializer = SerializadorAtributoClase(attribute)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='attributes/(?P<attr_name>[^/.]+)')
    def eliminar_atributo(self, request, pk=None, attr_name=None):
        """Eliminar atributo de la clase"""
        success = self.service.remove_attribute(pk, attr_name)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Attribute not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=['patch'])
    def actualizar_posicion(self, request, pk=None):
        """Actualizar posición de la clase"""
        class_entity = self.service.update_class_position(pk, request.data['position'])
        serializer = SerializadorEntidadClase(class_entity)
        return Response(serializer.data)
"""
Views module for diagram management
"""
from .diagram_viewset import DiagramViewSet
from .class_entity_viewset import ClassEntityViewSet  
from .relationship_viewset import RelationshipViewSet

# Legacy aliases
VistaConjuntoDiagramas = DiagramViewSet
VistaConjuntoEntidadesClase = ClassEntityViewSet
VistaConjuntoRelaciones = RelationshipViewSet

__all__ = [
    'DiagramViewSet',
    'ClassEntityViewSet', 
    'RelationshipViewSet',
    'VistaConjuntoDiagramas',
    'VistaConjuntoEntidadesClase',
    'VistaConjuntoRelaciones'
]
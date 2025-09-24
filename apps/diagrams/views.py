"""
Vistas de la API - Capa de Presentación
"""
from .controllers.controller_Diagramas import VistaConjuntoDiagramas
from .controllers.controller_EntidadClase import VistaConjuntoEntidadesClase
from .controllers.controller_Relaciones import VistaConjuntoRelaciones

# Alias para compatibilidad con urls.py
DiagramViewSet = VistaConjuntoDiagramas
ClassEntityViewSet = VistaConjuntoEntidadesClase
RelationshipViewSet = VistaConjuntoRelaciones

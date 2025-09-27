"""
Repositories module for diagram management
"""
from .diagrama_repository import DiagramRepository, RepositorioDiagrama
from .entidad_clase_repository import ClassEntityRepository, RepositorioEntidadClase
from .relacion_repository import RelationshipRepository, RepositorioRelacion

__all__ = [
    'DiagramRepository',
    'RepositorioDiagrama', 
    'ClassEntityRepository',
    'RepositorioEntidadClase',
    'RelationshipRepository',
    'RepositorioRelacion'
]
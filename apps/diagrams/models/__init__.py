"""
Models module for diagram management
"""
from .diagrama import Diagrama
from .entidad_clase import EntidadClase
from .atributo_clase import AtributoClase
from .relacion import Relacion

__all__ = [
    'Diagrama',
    'EntidadClase', 
    'AtributoClase',
    'Relacion'
]
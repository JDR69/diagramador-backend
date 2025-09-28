"""
Middleware personalizado para gestión de conexiones de base de datos.
"""
from django.db import connections
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class ConnectionCleanupMiddleware(MiddlewareMixin):
    """
    Middlewaree que cierra todas las conexiones de base de datos después de cada request.
    Esto es especialmente útil en servicios con límites estrictos de conexión como Render.
    """
    
    def process_response(self, request, response):
        """Cierra todas las conexiones después de procesar la respuesta."""
        try:
            # Cerrar todas las conexiones de base de datos
            for alias in connections:
                try:
                    connection = connections[alias]
                    if connection.connection is not None:
                        connection.close()
                        logger.debug(f"Conexión '{alias}' cerrada correctamente")
                except Exception as e:
                    logger.warning(f"Error cerrando conexión '{alias}': {e}")
        except Exception as e:
            logger.error(f"Error en limpieza de conexiones: {e}")
        
        return response
    
    def process_exception(self, request, exception):
        """Cierra conexiones incluso si hay una excepción."""
        try:
            for alias in connections:
                try:
                    connection = connections[alias]
                    if connection.connection is not None:
                        connection.close()
                        logger.debug(f"Conexión '{alias}' cerrada después de excepción")
                except Exception as e:
                    logger.warning(f"Error cerrando conexión '{alias}' tras excepción: {e}")
        except Exception as e:
            logger.error(f"Error en limpieza de conexiones tras excepción: {e}")
        
        return None  # Continúa con el manejo normal de excepciones
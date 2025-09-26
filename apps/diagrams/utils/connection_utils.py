"""
Decoradores y utilidades para gestión automática de conexiones de base de datos.
"""
import functools
import logging
from django.db import connections

logger = logging.getLogger(__name__)

def auto_close_connections(func):
    """
    Decorador que cierra automáticamente todas las conexiones de base de datos
    después de ejecutar la función, independientemente de si hay errores.
    
    Uso:
    @auto_close_connections
    def mi_vista(request):
        # código de la vista
        return response
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Cerrar todas las conexiones sin excepción
            try:
                for alias in connections:
                    connection = connections[alias]
                    if connection.connection is not None:
                        connection.close()
                        logger.debug(f"Conexión '{alias}' cerrada automáticamente")
            except Exception as e:
                logger.warning(f"Error cerrando conexiones automáticamente: {e}")
    
    return wrapper

def close_all_connections():
    """
    Función utilitaria para cerrar todas las conexiones de base de datos.
    Registra errores pero no los propaga.
    """
    try:
        for alias in connections:
            try:
                connection = connections[alias]
                if connection.connection is not None:
                    connection.close()
                    logger.debug(f"Conexión '{alias}' cerrada")
            except Exception as e:
                logger.warning(f"Error cerrando conexión '{alias}': {e}")
    except Exception as e:
        logger.error(f"Error general cerrando conexiones: {e}")

def get_connection_status():
    """
    Obtiene el estado de todas las conexiones de base de datos.
    
    Returns:
        dict: Diccionario con el estado de cada conexión
    """
    status = {}
    try:
        for alias in connections:
            try:
                connection = connections[alias]
                if connection.connection is not None:
                    # Intentar hacer una consulta simple
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                    status[alias] = "activa"
                else:
                    status[alias] = "cerrada"
            except Exception as e:
                status[alias] = f"error: {str(e)}"
    except Exception as e:
        logger.error(f"Error obteniendo estado de conexiones: {e}")
        status['error_general'] = str(e)
    
    return status
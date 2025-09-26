"""
Comando de gestión para cerrar todas las conexiones de base de datos.
Útil para liberar conexiones antes de hacer migraciones o cuando se detecta
que el servidor está llegando al límite de conexiones.
"""
from django.core.management.base import BaseCommand
from django.db import connections
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Cierra todas las conexiones de base de datos para liberar recursos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza el cierre de conexiones incluso si hay errores',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada del proceso',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        force = options.get('force', False)
        
        self.stdout.write(self.style.WARNING('Iniciando cierre de conexiones de base de datos...'))
        
        total_conexiones = 0
        cerradas_exitosamente = 0
        errores = 0
        
        for alias in connections:
            total_conexiones += 1
            try:
                connection = connections[alias]
                if connection.connection is not None:
                    if verbose:
                        self.stdout.write(f"Cerrando conexión '{alias}'...")
                    connection.close()
                    cerradas_exitosamente += 1
                    if verbose:
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Conexión '{alias}' cerrada exitosamente")
                        )
                else:
                    if verbose:
                        self.stdout.write(f"Conexión '{alias}' ya estaba cerrada")
                    
            except Exception as e:
                errores += 1
                error_msg = f"Error cerrando conexión '{alias}': {str(e)}"
                logger.error(error_msg)
                
                if force:
                    self.stdout.write(self.style.WARNING(f"⚠ {error_msg} (continuando por --force)"))
                else:
                    self.stdout.write(self.style.ERROR(f"✗ {error_msg}"))
                    if not force:
                        break
        
        # Resumen final
        self.stdout.write("")
        self.stdout.write(f"Resumen:")
        self.stdout.write(f"  Total de conexiones: {total_conexiones}")
        self.stdout.write(f"  Cerradas exitosamente: {cerradas_exitosamente}")
        self.stdout.write(f"  Errores encontrados: {errores}")
        
        if errores == 0:
            self.stdout.write(
                self.style.SUCCESS("✅ Todas las conexiones fueron cerradas exitosamente")
            )
        elif errores > 0 and force:
            self.stdout.write(
                self.style.WARNING("⚠ Proceso completado con errores (forzado)")
            )
        else:
            self.stdout.write(
                self.style.ERROR("❌ Proceso interrumpido por errores")
            )
            exit(1)
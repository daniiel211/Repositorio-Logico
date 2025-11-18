"""
Configuración de la aplicación asignacion
"""

from django.apps import AppConfig

class AsignacionConfig(AppConfig):
    """
    Configuración de la aplicación de asignaciones
    Define nombre y configuración específica de la app
    """
    
    # Nombre de la aplicación (debe coincidir con el nombre de la carpeta)
    name = 'apps.asignacion'
    
    # Nombre legible para la aplicación
    verbose_name = 'Gestión de Asignaciones'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista
        Se puede usar para señales o configuración adicional
        """
        pass
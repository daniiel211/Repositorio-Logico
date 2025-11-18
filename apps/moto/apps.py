"""
Configuración de la aplicación moto
"""

from django.apps import AppConfig

class MotoConfig(AppConfig):
    """
    Configuración de la aplicación de motos
    """
    
    name = 'apps.moto'
    verbose_name = 'Gestión de Motos'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista
        """
        pass
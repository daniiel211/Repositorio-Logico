"""
Configuración de la aplicación motorista
"""

from django.apps import AppConfig

class MotoristaConfig(AppConfig):
    """
    Configuración de la aplicación de motoristas
    """
    
    name = 'apps.motorista'
    verbose_name = 'Gestión de Motoristas'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista
        """
        pass
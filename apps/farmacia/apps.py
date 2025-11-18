"""
Configuración de la aplicación farmacia
"""

from django.apps import AppConfig

class FarmaciaConfig(AppConfig):
    """
    Configuración de la aplicación de farmacias
    """
    
    # Nombre de la aplicación (debe coincidir con INSTALLED_APPS)
    name = 'apps.farmacia'
    verbose_name = 'Gestión de Farmacias'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista
        """
        pass
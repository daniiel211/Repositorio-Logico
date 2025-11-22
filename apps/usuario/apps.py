from django.apps import AppConfig

class UsuarioConfig(AppConfig):
    """
    Configuración de la aplicación Usuario para Django.
    Define metadatos y comportamiento de la aplicación.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuario'  
    verbose_name = 'Gestión de Usuarios'
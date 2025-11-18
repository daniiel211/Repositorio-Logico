"""
Modelo Farmacia para la aplicación de farmacias
Define la estructura de datos para las farmacias del sistema
"""

from django.db import models
from django.conf import settings  # Importar settings para usar AUTH_USER_MODEL

class Farmacia(models.Model):
    """
    Modelo que representa una farmacia en el sistema
    Contiene información de ubicación, horarios y contactos
    """
    
    # Identificador único de la farmacia
    IdFarmacia = models.CharField(primary_key=True, max_length=10, verbose_name="ID Farmacia")
    
    # Información básica de la farmacia
    nombre = models.CharField(max_length=100, verbose_name="Nombre Farmacia")
    direccion = models.CharField(max_length=200, verbose_name="Dirección")
    comuna = models.CharField(max_length=50, verbose_name="Comuna")
    provincia = models.CharField(max_length=50, verbose_name="Provincia")
    region = models.CharField(max_length=50, verbose_name="Región")
    
    # Horarios de atención
    apertura = models.TimeField(verbose_name="Hora Apertura")
    cierre = models.TimeField(verbose_name="Hora Cierre")
    
    # Información de contacto
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    
    # Coordenadas geográficas
    latitud = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True, verbose_name="Latitud")
    longitud = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True, verbose_name="Longitud")
    
    # Campos de auditoría - CORREGIDO: usar settings.AUTH_USER_MODEL
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='farmacias_creadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='farmacias_modificadas'
    )
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Configuración meta del modelo Farmacia
        Define nombre de tabla, etiquetas y ordenamiento
        """
        verbose_name = "Farmacia"
        verbose_name_plural = "Farmacias"
        ordering = ['nombre']
        db_table = 'farmacia'

    def __str__(self):
        """
        Representación en string de la farmacia
        """
        return f"{self.nombre} - {self.direccion}"
    
    def soft_delete(self):
        """
        Marca la farmacia como inactiva (eliminación lógica)
        No elimina el registro de la base de datos
        """
        self.activo = False
        self.save()

    def reactivar(self):
        """
        Reactiva una farmacia previamente marcada como inactiva
        """
        self.activo = True
        self.save()
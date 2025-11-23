"""
Modelo Moto para la aplicación de motos
Define la estructura de datos para las motos del sistema con validaciones
"""

from django.db import models
from django.conf import settings  # Importar settings para usar AUTH_USER_MODEL
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import re

def validar_patente_chilena(value):
    """
    Valida formato de patente chilena
    Acepta formatos antiguos, nuevos y especiales
    """
    value = value.upper().replace('-', '').replace(' ', '')

    patrones = [
        re.compile(r'^[A-Z]{4}\d{2}$'),            # Formato nuevo: BBBB11
        re.compile(r'^[A-Z]{2}\d{4}$'),            # Formato antiguo: BB1122
        re.compile(r'^CD\d{4}$'),                  # Cuerpo diplomático
        re.compile(r'^CC\d{4}$'),                  # Cuerpo consular
        re.compile(r'^FFAA\d{3}$'),                # Fuerzas Armadas
        re.compile(r'^CARAB\d{4}$'),               # Carabineros
        re.compile(r'^PDI\d{4}$'),                 # Policía de Investigaciones
    ]
    
    if not any(re.match(patron, value) for patron in patrones):
        raise ValidationError('Formato de patente chilena inválido')

class MotoManager(models.Manager):
    """
    Manager personalizado para el modelo Moto
    Proporciona métodos de consulta específicos
    """
    
    def activas(self):
        """
        Retorna solo las motos activas
        """
        return self.filter(activo=True)
    
    def inactivas(self):
        """
        Retorna solo las motos inactivas
        """
        return self.filter(activo=False)

class Moto(models.Model):
    """
    Modelo que representa una moto en el sistema
    Contiene información técnica, documentación y estado
    """
    
    # Opciones para el campo propietario
    OPCIONES_PROPIETARIO = [
        ('EMPRESA', 'Empresa'),
        ('MOTORISTA', 'Motorista')
    ]

    # Identificación única de la moto
    patente = models.CharField(
        primary_key=True, 
        max_length=10,
        validators=[validar_patente_chilena],
        verbose_name='Patente'
    )
    
    # Información técnica
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.IntegerField(
        validators=[
            MinValueValidator(1900),  # Año mínimo válido
            MaxValueValidator(2099)   # Año máximo válido
        ],
        verbose_name='Año'
    )
    color = models.CharField(max_length=30)
    numChasis = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name='Número de Chasis'
    )
    motor = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name='Número de Motor'
    )
    
    # Información de propiedad
    propietario = models.CharField(
        max_length=50, 
        choices=OPCIONES_PROPIETARIO
    )
    
    # Documentación de la moto
    permisoCirculacion = models.FileField(
        upload_to='documentos/motos/permisos/',
        verbose_name='Permiso de Circulación'
    )
    seguro = models.FileField(
        upload_to='documentos/motos/seguros/',
        verbose_name='Póliza de Seguro'
    )
    revisionTecnica = models.FileField(
        upload_to='documentos/motos/revisiones/',
        verbose_name='Revisión Técnica'
    )
    
    # Campos de auditoría
    activo = models.BooleanField(default=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True,
        related_name='motos_creadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='motos_modificadas'
    )
    fecha_modificacion = models.DateTimeField(auto_now=True)

    # Usar el manager personalizado
    objects = MotoManager()

    class Meta:
        """
        Configuración meta del modelo Moto
        """
        # CORRECCIÓN: Quitar app_label si existe
        db_table = 'moto'
        verbose_name = 'Moto'
        verbose_name_plural = 'Motos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        """
        Representación en string de la moto
        """
        return f"{self.patente} - {self.marca} {self.modelo}"

    def soft_delete(self):
        """
        Marca la moto como inactiva (eliminación lógica)
        """
        self.activo = False
        self.save()

    def reactivar(self):
        """
        Reactiva una moto previamente marcada como inactiva
        """
        self.activo = True
        self.save()

    def documentos_completos(self):
        """
        Verifica si todos los documentos obligatorios están cargados
        Retorna True si todos los documentos están presentes
        """
        return all([
            self.permisoCirculacion,
            self.seguro,
            self.revisionTecnica
        ])
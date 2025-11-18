"""
Modelos para la aplicación de asignaciones
Define las relaciones entre motoristas, motos y farmacias
"""

from django.db import models
from django.conf import settings  # Importar settings para usar AUTH_USER_MODEL
from django.utils import timezone

class AsignacionMoto(models.Model):
    """
    Modelo que representa la asignación de una moto a un motorista
    Relaciona motorista, moto y usuario que realiza la asignación
    """
    
    # Constantes para estados de asignación
    ESTADO_ACTIVA = 'ACTIVA'
    ESTADO_FINALIZADA = 'FINALIZADA'
    ESTADO_SUSPENDIDA = 'SUSPENDIDA'
    
    # Opciones para el campo estado
    ESTADOS_ASIGNACION = [
        (ESTADO_ACTIVA, 'Activa'),
        (ESTADO_FINALIZADA, 'Finalizada'),
        (ESTADO_SUSPENDIDA, 'Suspendida'),
    ]
    
    # Relación con motorista (usando string para evitar import circular)
    motorista = models.ForeignKey('motorista.Motorista', on_delete=models.CASCADE)
    
    # Relación con moto (usando string para evitar import circular)
    moto = models.ForeignKey('moto.Moto', on_delete=models.CASCADE)
    
    # Estado actual de la asignación
    estado = models.CharField(max_length=20, choices=ESTADOS_ASIGNACION, default=ESTADO_ACTIVA)
    
    # Observaciones adicionales
    observaciones = models.TextField(blank=True, null=True)
    
    # Fecha de asignación (automática al crear)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    
    # Fecha de finalización (se establece al finalizar)
    fecha_finalizacion = models.DateTimeField(blank=True, null=True)
    
    # Campo para soft delete
    activo = models.BooleanField(default=True)
    
    # Usuario que creó la asignación
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='asignaciones_moto_creadas'
    )
    
    # Usuario que modificó la asignación
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='asignaciones_moto_modificadas'
    )
    
    # Fecha de creación y modificación
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Configuración adicional del modelo"""
        db_table = 'asignacion_moto'  # Nombre de tabla en BD
        permissions = [
            ("can_manage_asignaciones", "Puede gestionar asignaciones"),
        ]
    
    def __str__(self):
        """Representación en string del objeto"""
        return f"{self.motorista} - {self.moto}"
    
    def finalizar(self, usuario):
        """
        Método para finalizar la asignación
        Actualiza estado, fecha de finalización y usuario que modifica
        """
        self.estado = self.ESTADO_FINALIZADA
        self.fecha_finalizacion = timezone.now()
        self.modificado_por = usuario
        self.save()
    
    @property
    def duracion_asignacion(self):
        """
        Propiedad que calcula la duración de la asignación
        Retorna timedelta con la duración
        """
        if self.fecha_finalizacion:
            return self.fecha_finalizacion - self.fecha_asignacion
        return timezone.now() - self.fecha_asignacion

class AsignacionFarmacia(models.Model):
    """
    Modelo que representa la asignación de una farmacia a un motorista
    Relaciona motorista, farmacia y usuario que realiza la asignación
    """
    
    # Constantes para estados de asignación
    ESTADO_ACTIVA = 'ACTIVA'
    ESTADO_FINALIZADA = 'FINALIZADA'
    ESTADO_SUSPENDIDA = 'SUSPENDIDA'
    
    # Opciones para el campo estado
    ESTADOS_ASIGNACION = [
        (ESTADO_ACTIVA, 'Activa'),
        (ESTADO_FINALIZADA, 'Finalizada'),
        (ESTADO_SUSPENDIDA, 'Suspendida'),
    ]
    
    # Relación con motorista
    motorista = models.ForeignKey('motorista.Motorista', on_delete=models.CASCADE)
    
    # Relación con farmacia
    farmacia = models.ForeignKey('farmacia.Farmacia', on_delete=models.CASCADE)
    
    # Estado actual de la asignación
    estado = models.CharField(max_length=20, choices=ESTADOS_ASIGNACION, default=ESTADO_ACTIVA)
    
    # Observaciones adicionales
    observaciones = models.TextField(blank=True, null=True)
    
    # Fecha de asignación
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    
    # Fecha de finalización
    fecha_finalizacion = models.DateTimeField(blank=True, null=True)
    
    # Campo para soft delete
    activo = models.BooleanField(default=True)
    
    # Usuario que creó la asignación
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='asignaciones_farmacia_creadas'
    )
    
    # Usuario que modificó la asignación
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='asignaciones_farmacia_modificadas'
    )
    
    # Fecha de creación y modificación
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Configuración adicional del modelo"""
        db_table = 'asignacion_farmacia'
    
    def __str__(self):
        """Representación en string del objeto"""
        return f"{self.motorista} - {self.farmacia}"
    
    def finalizar(self, usuario):
        """
        Método para finalizar la asignación de farmacia
        """
        self.estado = self.ESTADO_FINALIZADA
        self.fecha_finalizacion = timezone.now()
        self.modificado_por = usuario
        self.save()
    
    @property
    def duracion_asignacion(self):
        """
        Propiedad que calcula la duración de la asignación
        """
        if self.fecha_finalizacion:
            return self.fecha_finalizacion - self.fecha_asignacion
        return timezone.now() - self.fecha_asignacion
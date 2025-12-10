# apps/configuracion/models.py - ARCHIVO CORREGIDO COMPLETO
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class RangoAccion(models.Model):
    """
    Define el rango de acción máximo para motoristas en relación a farmacias
    """
    
    farmacia = models.OneToOneField(
        'farmacia.Farmacia',
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='Farmacia',
        related_name='rango_accion'
    )
    
    distancia_maxima_km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name='Distancia Máxima (km)'
    )
    
    comunas_permitidas = models.TextField(
        blank=True,
        null=True,
        verbose_name='Comunas Permitidas',
        help_text='Lista de comunas separadas por coma donde puede operar el motorista'
    )
    
    horario_inicio = models.TimeField(
        default='08:00',
        verbose_name='Horario Inicio'
    )
    
    horario_fin = models.TimeField(
        default='22:00',
        verbose_name='Horario Fin'
    )
    
    activo = models.BooleanField(default=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='rangos_accion_creados'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rangos_accion_modificados'
    )
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'configuracion_rango_accion'
        verbose_name = 'Rango de Acción'
        verbose_name_plural = 'Rangos de Acción'
        # SIN PERMISOS PERSONALIZADOS - Django ya los crea automáticamente

    def __str__(self):
        return f"Rango - {self.farmacia.nombre} ({self.distancia_maxima_km}km)"

    @property
    def horario_operacion(self):
        return f"{self.horario_inicio.strftime('%H:%M')} - {self.horario_fin.strftime('%H:%M')}"

class TipoIncidencia(models.Model):
    """
    Catálogo de tipos de incidencias posibles
    """
    
    codigo = models.CharField(max_length=10, primary_key=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(verbose_name='Descripción')
    gravedad = models.CharField(
        max_length=20,
        choices=[
            ('BAJA', 'Baja'),
            ('MEDIA', 'Media'),
            ('ALTA', 'Alta'),
            ('CRITICA', 'Crítica')
        ],
        default='MEDIA',
        verbose_name='Nivel de Gravedad'
    )
    
    requiere_autorizacion = models.BooleanField(
        default=False,
        verbose_name='Requiere Autorización'
    )
    
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'configuracion_tipo_incidencia'
        verbose_name = 'Tipo de Incidencia'
        verbose_name_plural = 'Tipos de Incidencia'
        # SIN PERMISOS PERSONALIZADOS - Django ya los crea automáticamente

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class IncidenciaMovimiento(models.Model):
    """
    Registro de incidencias ocurridas en los movimientos
    """
    
    movimiento = models.ForeignKey(
        'movimiento.Movimiento',
        on_delete=models.CASCADE,
        related_name='incidencias',
        verbose_name='Movimiento'
    )
    
    tipo_incidencia = models.ForeignKey(
        TipoIncidencia,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Incidencia'
    )
    
    ESTADOS_INCIDENCIA = [
        ('REGISTRADA', 'Registrada'),
        ('EN_REVISION', 'En Revisión'),
        ('RESUELTA', 'Resuelta'),
        ('ESCALADA', 'Escalada'),
        ('CERRADA', 'Cerrada')
    ]
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_INCIDENCIA,
        default='REGISTRADA',
        verbose_name='Estado'
    )
    
    descripcion = models.TextField(verbose_name='Descripción de la Incidencia')
    
    evidencia = models.FileField(
        upload_to='incidencias/evidencias/',
        null=True,
        blank=True,
        verbose_name='Evidencia'
    )
    
    fecha_incidencia = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Incidencia'
    )
    
    fecha_resolucion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Resolución'
    )
    
    resolucion = models.TextField(
        null=True,
        blank=True,
        verbose_name='Resolución'
    )
    
    # Campos de auditoría
    reportada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='incidencias_reportadas',
        verbose_name='Reportada por'
    )
    
    asignada_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias_asignadas',
        verbose_name='Asignada a'
    )
    
    resuelta_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias_resueltas',
        verbose_name='Resuelta por'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'configuracion_incidencia_movimiento'
        verbose_name = 'Incidencia de Movimiento'
        verbose_name_plural = 'Incidencias de Movimiento'
        ordering = ['-fecha_incidencia']
        # SIN PERMISOS PERSONALIZADOS - Django ya los crea automáticamente

    def __str__(self):
        return f"Incidencia #{self.id} - {self.movimiento.idMovimiento}"

    def marcar_como_resuelta(self, usuario, resolucion):
        """Marca la incidencia como resuelta"""
        self.estado = 'RESUELTA'
        self.resuelta_por = usuario
        self.resolucion = resolucion
        self.fecha_resolucion = timezone.now()
        self.save()

    @property
    def tiempo_resolucion(self):
        """Calcula el tiempo que tomó resolver la incidencia"""
        if self.fecha_resolucion and self.fecha_incidencia:
            return self.fecha_resolucion - self.fecha_incidencia
        return None

class ConfiguracionSistema(models.Model):
    """
    Configuraciones generales del sistema
    """
    
    clave = models.CharField(max_length=50, primary_key=True, verbose_name='Clave')
    valor = models.TextField(verbose_name='Valor')
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('TEXTO', 'Texto'),
            ('NUMERO', 'Número'),
            ('BOOLEANO', 'Booleano'),
            ('JSON', 'JSON')
        ],
        default='TEXTO',
        verbose_name='Tipo de Dato'
    )
    
    descripcion = models.TextField(verbose_name='Descripción')
    editable = models.BooleanField(default=True, verbose_name='Editable')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'configuracion_sistema'
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
        # SIN PERMISOS PERSONALIZADOS - Django ya los crea automáticamente

    def __str__(self):
        return f"{self.clave} = {self.valor}"

    def get_valor_typed(self):
        """Retorna el valor convertido al tipo correspondiente"""
        if self.tipo == 'NUMERO':
            try:
                return float(self.valor) if '.' in self.valor else int(self.valor)
            except ValueError:
                return self.valor
        elif self.tipo == 'BOOLEANO':
            return self.valor.lower() in ('true', '1', 'yes', 'si')
        elif self.tipo == 'JSON':
            try:
                import json
                return json.loads(self.valor)
            except json.JSONDecodeError:
                return self.valor
        else:
            return self.valor
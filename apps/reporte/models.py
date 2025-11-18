from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ConfiguracionReporte(models.Model):
    """Configuración general para reportes del sistema"""
    
    TIPO_REPORTE_CHOICES = [
        ('farmacia', 'Farmacias'),
        ('motorista', 'Motoristas'),
        ('moto', 'Motos'),
        ('asignacion', 'Asignaciones'),
        ('movimiento', 'Movimientos'),
    ]
    
    FORMATO_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo_reporte = models.CharField(max_length=20, choices=TIPO_REPORTE_CHOICES)
    formato_salida = models.CharField(max_length=10, choices=FORMATO_CHOICES, default='pdf')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'configuracion_reporte'
        verbose_name = 'Configuración de Reporte'
        verbose_name_plural = 'Configuraciones de Reportes'

    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_reporte_display()}"

class FiltroReporte(models.Model):
    """Almacena filtros aplicados a reportes"""
    
    configuracion = models.ForeignKey(ConfiguracionReporte, on_delete=models.CASCADE)
    nombre_filtro = models.CharField(max_length=50)
    valor_filtro = models.TextField()
    tipo_filtro = models.CharField(max_length=30)
    
    class Meta:
        db_table = 'filtro_reporte'

class ReporteGenerado(models.Model):
    """Registro de reportes generados"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('error', 'Error'),
    ]
    
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE)
    tipo_reporte = models.CharField(max_length=20, choices=ConfiguracionReporte.TIPO_REPORTE_CHOICES)
    nombre_archivo = models.CharField(max_length=255)
    formato = models.CharField(max_length=10, choices=ConfiguracionReporte.FORMATO_CHOICES)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    filtros_aplicados = models.JSONField(default=dict)  # Almacena filtros en formato JSON
    
    class Meta:
        db_table = 'reporte_generado'
        verbose_name = 'Reporte Generado'
        verbose_name_plural = 'Reportes Generados'
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"Reporte {self.tipo_reporte} - {self.fecha_generacion.strftime('%Y-%m-%d %H:%M')}"
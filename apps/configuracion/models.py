from django.db import models
from django.utils import timezone

class RangoOperacion(models.Model):
    """Configuración del área de cobertura para cada farmacia"""
    idRango = models.AutoField(primary_key=True)
    idFarmacia = models.ForeignKey('farmacia.Farmacia', on_delete=models.CASCADE, related_name='rangos_operacion', db_column='idFarmacia')
    radioKm = models.DecimalField(max_digits=5, decimal_places=2)
    fechaConfiguracion = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'RANGO_OPERACION'
        verbose_name = 'Rango de Operación'
        verbose_name_plural = 'Rangos de Operación'

    def __str__(self):
        return f"Rango {self.idRango} - {self.idFarmacia.nombre} ({self.radioKm} km)"

class Incidencia(models.Model):
    """Problemas o eventos durante la ejecución de movimientos"""
    idIncidencia = models.AutoField(primary_key=True)
    idMovimiento = models.ForeignKey('movimiento.Movimiento', on_delete=models.CASCADE, related_name='incidencias', db_column='idMovimiento')
    tipoIncidencia = models.CharField(max_length=50)
    descripcion = models.TextField()
    fechaReporte = models.DateTimeField(default=timezone.now)
    resuelta = models.BooleanField(default=False)

    class Meta:
        db_table = 'INCIDENCIA'
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'

    def __str__(self):
        return f"Incidencia #{self.idIncidencia} - {self.tipoIncidencia}"
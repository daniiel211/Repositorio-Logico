from django.db import models
from django.utils import timezone

class EstadoMovimiento(models.Model):
    """Catálogo de estados posibles para los movimientos"""
    codigo_estado = models.CharField(primary_key=True, max_length=3)
    nombre_estado = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'ESTADOS_MOVIMIENTO'
        verbose_name = 'Estado de Movimiento'
        verbose_name_plural = 'Estados de Movimiento'

    def __str__(self):
        return f"{self.codigo_estado} - {self.nombre_estado}"

class Movimiento(models.Model):
    """Core del sistema - representa cada acción de entrega/traslado"""
    
    TIPO_MOVIMIENTO_CHOICES = [
        ('directo', 'Directo'),
        ('receta', 'Receta'),
        ('traslado', 'Traslado'),
        ('reenvio', 'Reenvío'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_camino', 'En Camino'),
        ('entregado', 'Entregado'),
        ('fallido', 'Fallido'),
        ('anulado', 'Anulado'),
        ('pendiente_autorizacion', 'Pendiente Autorización'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('pos', 'POS'),
    ]

    # Clave Primaria
    idMovimiento = models.AutoField(primary_key=True)
    
    # Claves Foráneas
    idFarmaciaOrigen = models.ForeignKey('farmacia.Farmacia', on_delete=models.PROTECT, related_name='movimientos_origen', db_column='idFarmaciaOrigen')
    idFarmaciaDestino = models.ForeignKey('farmacia.Farmacia', on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_destino', db_column='idFarmaciaDestino')
    rutMotorista = models.ForeignKey('motorista.Motorista', on_delete=models.PROTECT, related_name='movimientos', db_column='rutMotorista')
    creado_por = models.ForeignKey('usuario.Usuario', on_delete=models.PROTECT, related_name='movimientos_creados', null=True)
    autorizadoPor = models.ForeignKey('usuario.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_autorizados', db_column='autorizadoPor')
    movimientoOrigen = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='reenvios_posteriores', db_column='movimientoOrigen')
    
    # Campos Propios
    tipoMovimiento = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO_CHOICES)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='pendiente')
    fechaCreacion = models.DateTimeField(default=timezone.now)
    fechaEntrega = models.DateTimeField(null=True, blank=True)
    direccionDestino = models.CharField(max_length=100, null=True, blank=True)
    clienteNombre = models.CharField(max_length=100, null=True, blank=True)
    clienteTelefono = models.CharField(max_length=20, null=True, blank=True)
    requiereReceta = models.BooleanField(default=False)
    recetaRetirada = models.BooleanField(default=False)
    metodoPago = models.CharField(max_length=10, choices=METODO_PAGO_CHOICES, null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    requiereAutorizacion = models.BooleanField(default=False)
    fechaAutorizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'MOVIMIENTO'
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'

    def __str__(self):
        return f"Movimiento #{self.idMovimiento} - {self.tipoMovimiento}"

class MovimientoDirecto(models.Model):
    """Movimientos directos (Local → Domicilio)"""
    movimiento = models.OneToOneField(
        Movimiento, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        related_name='directo'
    )
    
    # Campos Propios
    direccionEntrega = models.CharField(max_length=255)
    comunaEntrega = models.CharField(max_length=100)
    telefonoCliente = models.CharField(max_length=20)
    producto = models.CharField(max_length=255)
    instrucciones = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'MOVIMIENTO_DIRECTO'
        verbose_name = 'Movimiento Directo'
        verbose_name_plural = 'Movimientos Directos'

    def __str__(self):
        return f"Directo de Movimiento #{self.movimiento.idMovimiento}"

class MovimientoReceta(models.Model):
    """Movimientos con receta (Domicilio → Local → Domicilio)"""
    movimiento = models.OneToOneField(
        Movimiento, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        related_name='receta'
    )
    
    # Campos Propios
    direccionEntrega = models.CharField(max_length=255)
    comunaEntrega = models.CharField(max_length=100)
    telefonoCliente = models.CharField(max_length=20)
    producto = models.CharField(max_length=255)
    archivoReceta = models.FileField(upload_to='recetas/', null=True, blank=True)
    requiereRetiroReceta = models.BooleanField(default=False)
    recetaRetirada = models.BooleanField(default=False)
    observaciones = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'MOVIMIENTO_RECETA'
        verbose_name = 'Movimiento Receta'
        verbose_name_plural = 'Movimientos Receta'

    def __str__(self):
        return f"Receta de Movimiento #{self.movimiento.idMovimiento}"

class MovimientoTraslado(models.Model):
    """Movimientos con traslado (Local → Local)"""
    movimiento = models.OneToOneField(
        Movimiento, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        related_name='traslado'
    )
    
    # Campos Propios
    producto = models.CharField(max_length=255)
    cantidad = models.IntegerField()
    motivoTraslado = models.CharField(max_length=255)
    observaciones = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'MOVIMIENTO_TRASLADO'
        verbose_name = 'Movimiento Traslado'
        verbose_name_plural = 'Movimientos Traslado'

    def __str__(self):
        return f"Traslado de Movimiento #{self.movimiento.idMovimiento}"

class MovimientoReenvio(models.Model):
    """Reenvíos por fallas de entrega"""
    movimiento = models.OneToOneField(
        Movimiento, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        related_name='reenvio'
    )
    
    # Claves Foráneas
    movimientoOriginal = models.ForeignKey(
        Movimiento, 
        on_delete=models.PROTECT, 
        related_name='reenvios'
    )
    
    # Campos Propios
    motivoReenvio = models.CharField(max_length=255)
    nuevaDireccion = models.CharField(max_length=255)
    nuevaFecha = models.DateTimeField()
    observaciones = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'MOVIMIENTO_REENVIO'
        verbose_name = 'Movimiento Reenvío'
        verbose_name_plural = 'Movimientos Reenvío'

    def __str__(self):
        return f"Reenvío de Movimiento #{self.movimiento.idMovimiento}"

class BitacoraMovimiento(models.Model):
    """Bitácora para auditoría de cambios en movimientos"""
    idBitacora = models.AutoField(primary_key=True)
    movimiento = models.ForeignKey(Movimiento, on_delete=models.CASCADE, related_name='bitacora')
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.PROTECT, related_name='registros_bitacora')
    fechaCambio = models.DateTimeField(default=timezone.now)
    estadoAnterior = models.CharField(max_length=50)
    estadoNuevo = models.CharField(max_length=50)
    observaciones = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'BITACORA_MOVIMIENTO'
        verbose_name = 'Bitácora de Movimiento'
        verbose_name_plural = 'Bitácoras de Movimiento'

    def __str__(self):
        return f"Bitácora #{self.idBitacora} - Movimiento #{self.movimiento.idMovimiento}"
from django.db import models
from django.utils import timezone
import uuid

class OrdenDespacho(models.Model):
    """
    Modelo para agrupar movimientos relacionados bajo un número de orden único
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('parcialmente_entregado', 'Parcialmente Entregado'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('cancelado', 'Cancelado'),
    ]
    
    idOrden = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_orden = models.CharField(max_length=20, unique=True, verbose_name="Número de Orden")
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Relación con la compra online (puede ser extendida para integración con APIs externas)
    id_compra_online = models.CharField(max_length=100, null=True, blank=True, verbose_name="ID Compra Online")
    cliente_nombre = models.CharField(max_length=100)
    cliente_telefono = models.CharField(max_length=20)
    cliente_email = models.EmailField(null=True, blank=True)
    
    # Dirección de entrega principal
    direccion_entrega = models.CharField(max_length=255)
    comuna_entrega = models.CharField(max_length=100)
    
    # Información de pago
    metodo_pago = models.CharField(max_length=20, choices=[
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('online', 'Online'),
    ])
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    observaciones = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'ORDEN_DESPACHO'
        verbose_name = 'Orden de Despacho'
        verbose_name_plural = 'Órdenes de Despacho'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Orden #{self.numero_orden} - {self.cliente_nombre}"

    def save(self, *args, **kwargs):
        if not self.numero_orden:
            # Generar número de orden automático: OD-YYYYMMDD-XXXX
            fecha_actual = timezone.now().strftime('%Y%m%d')
            ultima_orden = OrdenDespacho.objects.filter(
                numero_orden__startswith=f'OD-{fecha_actual}-'
            ).order_by('-numero_orden').first()
            
            if ultima_orden:
                ultimo_numero = int(ultima_orden.numero_orden.split('-')[-1])
                nuevo_numero = ultimo_numero + 1
            else:
                nuevo_numero = 1
                
            self.numero_orden = f'OD-{fecha_actual}-{nuevo_numero:04d}'
        
        super().save(*args, **kwargs)
    
    def actualizar_estado(self):
        """Actualiza el estado de la orden basado en los movimientos asociados"""
        movimientos = self.movimientos.all()
        
        if not movimientos:
            self.estado = 'pendiente'
        elif all(m.estado == 'entregado' for m in movimientos):
            self.estado = 'completado'
        elif any(m.estado == 'entregado' for m in movimientos):
            self.estado = 'parcialmente_entregado'
        elif any(m.estado in ['en_camino', 'pendiente'] for m in movimientos):
            self.estado = 'en_proceso'
        elif all(m.estado in ['fallido', 'anulado'] for m in movimientos):
            self.estado = 'fallido'
        
        self.save()
    
    @property
    def movimientos_entregados(self):
        return self.movimientos.filter(estado='entregado').count()
    
    @property
    def movimientos_totales(self):
        return self.movimientos.count()
    
    @property
    def porcentaje_completado(self):
        if self.movimientos_totales == 0:
            return 0
        return (self.movimientos_entregados / self.movimientos_totales) * 100


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
    
    # Nueva relación con Orden de Despacho
    orden_despacho = models.ForeignKey(
        OrdenDespacho, 
        on_delete=models.CASCADE, 
        related_name='movimientos',
        null=True, 
        blank=True,
        verbose_name="Orden de Despacho"
    )
    
    # Claves Foráneas existentes
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

    # Nuevos campos para trazabilidad mejorada
    producto = models.CharField(max_length=255, null=True, blank=True, verbose_name="Producto(s)")
    cantidad = models.IntegerField(default=1, verbose_name="Cantidad")
    prioridad = models.IntegerField(default=1, choices=[(1, 'Normal'), (2, 'Alta'), (3, 'Urgente')])
    intentos_entrega = models.IntegerField(default=0, verbose_name="Intentos de Entrega")

    class Meta:
        db_table = 'MOVIMIENTO'
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'
        ordering = ['-fechaCreacion']

    def __str__(self):
        orden_info = f" - Orden: {self.orden_despacho.numero_orden}" if self.orden_despacho else ""
        return f"Movimiento #{self.idMovimiento} - {self.tipoMovimiento}{orden_info}"

    def save(self, *args, **kwargs):
        # Si es un reenvío, incrementar intentos de entrega del movimiento original
        if self.tipoMovimiento == 'reenvio' and self.movimientoOrigen:
            self.movimientoOrigen.intentos_entrega += 1
            self.movimientoOrigen.save()
            
        super().save(*args, **kwargs)
        
        # Actualizar estado de la orden de despacho si existe
        if self.orden_despacho:
            self.orden_despacho.actualizar_estado()

    def crear_reenvio(self, motivo, nueva_direccion, nueva_fecha, usuario):
        """Método para crear un reenvío automáticamente"""
        from django.utils import timezone
        
        # Crear nuevo movimiento de reenvío
        nuevo_movimiento = Movimiento.objects.create(
            tipoMovimiento='reenvio',
            estado='pendiente',
            orden_despacho=self.orden_despacho,
            idFarmaciaOrigen=self.idFarmaciaOrigen,
            rutMotorista=self.rutMotorista,
            clienteNombre=self.clienteNombre,
            clienteTelefono=self.clienteTelefono,
            creado_por=usuario,
            metodoPago=self.metodoPago,
            monto=self.monto,
            movimientoOrigen=self,
            direccionDestino=nueva_direccion,
            producto=self.producto,
            cantidad=self.cantidad,
            prioridad=self.prioridad + 1,  # Aumentar prioridad en reenvíos
        )
        
        # Crear registro específico de reenvío
        from .models import MovimientoReenvio  # Importación local para evitar referencia circular
        MovimientoReenvio.objects.create(
            movimiento=nuevo_movimiento,
            movimientoOriginal=self,
            motivoReenvio=motivo,
            nuevaDireccion=nueva_direccion,
            nuevaFecha=nueva_fecha,
            observaciones=f"Reenvío automático por falla en entrega. Motivo: {motivo}"
        )
        
        # Actualizar estado del movimiento original
        self.estado = 'fallido'
        self.observaciones = f"{self.observaciones or ''}\nReenviado con nuevo ID: {nuevo_movimiento.idMovimiento}. Motivo: {motivo}"
        self.save()
        
        return nuevo_movimiento

    @property
    def es_primera_entrega(self):
        """Verifica si es el primer intento de entrega para esta orden"""
        if not self.orden_despacho:
            return True
        return self.orden_despacho.movimientos.filter(
            fechaCreacion__lt=self.fechaCreacion
        ).count() == 0


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
    producto = models.CharField(max_length=255)  # Ya existe, mantener
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
from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import OrdenDespacho, Movimiento, MovimientoDirecto, MovimientoReceta, MovimientoTraslado, MovimientoReenvio, BitacoraMovimiento
from apps.farmacia.models import Farmacia
from apps.motorista.models import Motorista
from apps.asignacion.models import AsignacionFarmacia


class OrdenDespachoForm(forms.ModelForm):
    """Formulario para crear órdenes de despacho"""
    
    class Meta:
        model = OrdenDespacho
        fields = [
            'id_compra_online', 'cliente_nombre', 'cliente_telefono', 'cliente_email',
            'direccion_entrega', 'comuna_entrega', 'metodo_pago', 'monto_total', 'observaciones'
        ]
        widgets = {
            'cliente_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
            'cliente_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono del cliente'}),
            'cliente_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email del cliente'}),
            'direccion_entrega': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección de entrega'}),
            'comuna_entrega': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comuna'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'monto_total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'id_compra_online': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID Compra Online (opcional)'}),
        }

    def clean_monto_total(self):
        monto = self.cleaned_data.get('monto_total')
        if monto is not None and monto <= 0:
            raise ValidationError("El monto total debe ser mayor a cero.")
        return monto


class MovimientoBaseForm(forms.ModelForm):
    """
    Formulario base con campos comunes para la mayoría de los movimientos.
    Ahora incluye relación con orden de despacho y filtro de motoristas por farmacia.
    """
    orden_despacho = forms.ModelChoiceField(
        queryset=OrdenDespacho.objects.filter(activo=True, estado__in=['pendiente', 'en_proceso']),
        label="Orden de Despacho",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    idFarmaciaOrigen = forms.ModelChoiceField(
        queryset=Farmacia.objects.filter(activo=True),
        label="Farmacia de Origen",
        widget=forms.Select(attrs={'class': 'form-control select2', 'onchange': 'filtrarMotoristas(this.value)'})
    )
    
    # Campo motorista se inicializa vacío y se llena dinámicamente
    rutMotorista = forms.ModelChoiceField(
        queryset=Motorista.objects.none(),
        label="Motorista Asignado",
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_rutMotorista'})
    )
    
    producto = forms.CharField(
        label="Producto(s)",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    cantidad = forms.IntegerField(
        label="Cantidad",
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    prioridad = forms.ChoiceField(
        choices=[(1, 'Normal'), (2, 'Alta'), (3, 'Urgente')],
        initial=1,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Movimiento
        fields = [
            'orden_despacho', 'idFarmaciaOrigen', 'rutMotorista', 'producto', 'cantidad', 'prioridad',
            'clienteNombre', 'clienteTelefono', 'metodoPago', 'monto', 'observaciones'
        ]
        widgets = {
            'clienteNombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
            'clienteTelefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono del cliente'}),
            'metodoPago': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # CORRECCIÓN: Verificar si la instancia existe y tiene idFarmaciaOrigen asignado
        if self.instance and self.instance.pk and self.instance.idFarmaciaOrigen:
            farmacia = self.instance.idFarmaciaOrigen
            motoristas_disponibles = self._obtener_motoristas_por_farmacia(farmacia.id)
            self.fields['rutMotorista'].queryset = motoristas_disponibles
        else:
            # Para instancias nuevas, inicializar con queryset vacío
            self.fields['rutMotorista'].queryset = Motorista.objects.none()

    def _obtener_motoristas_por_farmacia(self, farmacia_id):
        """Obtiene los motoristas asignados a una farmacia específica"""
        asignaciones_activas = AsignacionFarmacia.objects.filter(
            farmacia_id=farmacia_id,
            estado='ACTIVA',
            activo=True
        ).select_related('motorista')
        
        motoristas_ids = [asignacion.motorista.id for asignacion in asignaciones_activas]
        return Motorista.objects.filter(id__in=motoristas_ids, activo=True)

    def clean(self):
        cleaned_data = super().clean()
        orden_despacho = cleaned_data.get('orden_despacho')
        idFarmaciaOrigen = cleaned_data.get('idFarmaciaOrigen')
        rutMotorista = cleaned_data.get('rutMotorista')
        cliente_nombre = cleaned_data.get('clienteNombre')
        cliente_telefono = cleaned_data.get('clienteTelefono')

        # Validar que el motorista pertenezca a la farmacia seleccionada
        if idFarmaciaOrigen and rutMotorista:
            motoristas_permitidos = self._obtener_motoristas_por_farmacia(idFarmaciaOrigen.id)
            if rutMotorista not in motoristas_permitidos:
                self.add_error('rutMotorista', 
                    f"El motorista seleccionado no está asignado a la farmacia {idFarmaciaOrigen.nombre}")

        # Si hay orden de despacho, validar consistencia de datos
        if orden_despacho:
            if cliente_nombre and cliente_nombre != orden_despacho.cliente_nombre:
                self.add_error('clienteNombre', 
                    f"El nombre del cliente debe coincidir con la orden: {orden_despacho.cliente_nombre}")
            
            if cliente_telefono and cliente_telefono != orden_despacho.cliente_telefono:
                self.add_error('clienteTelefono',
                    f"El teléfono debe coincidir con la orden: {orden_despacho.cliente_telefono}")

        return cleaned_data

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is not None and monto < 0:
            raise ValidationError("El monto no puede ser negativo.")
        return monto


class MovimientoDirectoForm(MovimientoBaseForm):
    """Formulario para crear un Movimiento de tipo Directo."""
    direccionEntrega = forms.CharField(
        label="Dirección de Entrega", 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    comunaEntrega = forms.CharField(
        label="Comuna", 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    instrucciones = forms.CharField(
        label="Instrucciones Adicionales", 
        required=False, 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta(MovimientoBaseForm.Meta):
        fields = MovimientoBaseForm.Meta.fields + [
            'direccionEntrega', 'comunaEntrega', 'instrucciones'
        ]

    def clean(self):
        cleaned_data = super().clean()
        orden_despacho = cleaned_data.get('orden_despacho')
        direccion_entrega = cleaned_data.get('direccionEntrega')
        comuna_entrega = cleaned_data.get('comunaEntrega')

        # Si hay orden de despacho, usar la dirección de la orden
        if orden_despacho:
            if direccion_entrega != orden_despacho.direccion_entrega:
                self.add_error('direccionEntrega',
                    f"La dirección debe coincidir con la orden: {orden_despacho.direccion_entrega}")
            if comuna_entrega != orden_despacho.comuna_entrega:
                self.add_error('comunaEntrega',
                    f"La comuna debe coincidir con la orden: {orden_despacho.comuna_entrega}")

        return cleaned_data

    def save(self, commit=True, autor=None):
        with transaction.atomic():
            # Crear el objeto Movimiento base
            movimiento = super().save(commit=False)
            movimiento.tipoMovimiento = 'directo'
            movimiento.creado_por = autor
            movimiento.direccionDestino = self.cleaned_data['direccionEntrega']
            
            if commit:
                movimiento.save()

            # Crear el objeto MovimientoDirecto relacionado
            MovimientoDirecto.objects.create(
                movimiento=movimiento,
                direccionEntrega=self.cleaned_data['direccionEntrega'],
                comunaEntrega=self.cleaned_data['comunaEntrega'],
                telefonoCliente=self.cleaned_data['clienteTelefono'],
                producto=self.cleaned_data['producto'],
                instrucciones=self.cleaned_data['instrucciones']
            )
        return movimiento


class MovimientoRecetaForm(MovimientoBaseForm):
    """Formulario para crear un Movimiento de tipo Receta."""
    direccionEntrega = forms.CharField(
        label="Dirección de Entrega", 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    comunaEntrega = forms.CharField(
        label="Comuna", 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    archivoReceta = forms.FileField(
        label="Archivo de Receta", 
        required=False, 
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )
    requiereRetiroReceta = forms.BooleanField(
        label="Requiere retiro de receta física", 
        required=False
    )

    class Meta(MovimientoBaseForm.Meta):
        fields = MovimientoBaseForm.Meta.fields + [
            'direccionEntrega', 'comunaEntrega', 'archivoReceta', 'requiereRetiroReceta'
        ]

    def clean(self):
        cleaned_data = super().clean()
        orden_despacho = cleaned_data.get('orden_despacho')
        direccion_entrega = cleaned_data.get('direccionEntrega')
        comuna_entrega = cleaned_data.get('comunaEntrega')

        # Si hay orden de despacho, usar la dirección de la orden
        if orden_despacho:
            if direccion_entrega != orden_despacho.direccion_entrega:
                self.add_error('direccionEntrega',
                    f"La dirección debe coincidir con la orden: {orden_despacho.direccion_entrega}")
            if comuna_entrega != orden_despacho.comuna_entrega:
                self.add_error('comunaEntrega',
                    f"La comuna debe coincidir con la orden: {orden_despacho.comuna_entrega}")

        return cleaned_data

    def save(self, commit=True, autor=None):
        with transaction.atomic():
            movimiento = super().save(commit=False)
            movimiento.tipoMovimiento = 'receta'
            movimiento.requiereReceta = True
            movimiento.creado_por = autor
            movimiento.direccionDestino = self.cleaned_data['direccionEntrega']
            if commit:
                movimiento.save()

            MovimientoReceta.objects.create(
                movimiento=movimiento,
                direccionEntrega=self.cleaned_data['direccionEntrega'],
                comunaEntrega=self.cleaned_data['comunaEntrega'],
                telefonoCliente=self.cleaned_data['clienteTelefono'],
                producto=self.cleaned_data['producto'],
                archivoReceta=self.cleaned_data['archivoReceta'],
                requiereRetiroReceta=self.cleaned_data['requiereRetiroReceta'],
                observaciones=self.cleaned_data['observaciones']
            )
        return movimiento


class MovimientoTrasladoForm(forms.ModelForm):
    """Formulario para crear un Movimiento de tipo Traslado."""
    orden_despacho = forms.ModelChoiceField(
        queryset=OrdenDespacho.objects.filter(activo=True, estado__in=['pendiente', 'en_proceso']),
        label="Orden de Despacho",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    idFarmaciaOrigen = forms.ModelChoiceField(
        queryset=Farmacia.objects.filter(activo=True), 
        label="Farmacia de Origen", 
        widget=forms.Select(attrs={'class': 'form-control select2', 'onchange': 'filtrarMotoristas(this.value)'})
    )
    idFarmaciaDestino = forms.ModelChoiceField(
        queryset=Farmacia.objects.filter(activo=True), 
        label="Farmacia de Destino", 
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    
    # Campo motorista se inicializa vacío y se llena dinámicamente
    rutMotorista = forms.ModelChoiceField(
        queryset=Motorista.objects.none(),
        label="Motorista",
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_rutMotorista'})
    )
    
    producto = forms.CharField(
        label="Producto(s)",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    cantidad = forms.IntegerField(
        label="Cantidad",
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    prioridad = forms.ChoiceField(
        choices=[(1, 'Normal'), (2, 'Alta'), (3, 'Urgente')],
        initial=1,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = MovimientoTraslado
        fields = ['producto', 'cantidad', 'motivoTraslado', 'observaciones']
        widgets = {
            'producto': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'motivoTraslado': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # CORRECCIÓN: Verificar si la instancia existe y tiene movimiento con idFarmaciaOrigen
        if (self.instance and self.instance.pk and hasattr(self.instance, 'movimiento') 
            and self.instance.movimiento and self.instance.movimiento.idFarmaciaOrigen):
            farmacia = self.instance.movimiento.idFarmaciaOrigen
            motoristas_disponibles = self._obtener_motoristas_por_farmacia(farmacia.id)
            self.fields['rutMotorista'].queryset = motoristas_disponibles
        else:
            # Para instancias nuevas, inicializar con queryset vacío
            self.fields['rutMotorista'].queryset = Motorista.objects.none()

    def _obtener_motoristas_por_farmacia(self, farmacia_id):
        """Obtiene los motoristas asignados a una farmacia específica"""
        asignaciones_activas = AsignacionFarmacia.objects.filter(
            farmacia_id=farmacia_id,
            estado='ACTIVA',
            activo=True
        ).select_related('motorista')
        
        motoristas_ids = [asignacion.motorista.id for asignacion in asignaciones_activas]
        return Motorista.objects.filter(id__in=motoristas_ids, activo=True)

    def clean(self):
        cleaned_data = super().clean()
        origen = cleaned_data.get("idFarmaciaOrigen")
        destino = cleaned_data.get("idFarmaciaDestino")
        rutMotorista = cleaned_data.get("rutMotorista")

        if origen and destino and origen == destino:
            raise ValidationError("La farmacia de origen y destino no pueden ser la misma.")

        # Validar que el motorista pertenezca a la farmacia de origen
        if origen and rutMotorista:
            motoristas_permitidos = self._obtener_motoristas_por_farmacia(origen.id)
            if rutMotorista not in motoristas_permitidos:
                self.add_error('rutMotorista', 
                    f"El motorista seleccionado no está asignado a la farmacia {origen.nombre}")

        return cleaned_data

    def save(self, commit=True, autor=None):
        with transaction.atomic():
            # Crear movimiento base
            movimiento = Movimiento.objects.create(
                orden_despacho=self.cleaned_data['orden_despacho'],
                idFarmaciaOrigen=self.cleaned_data['idFarmaciaOrigen'],
                idFarmaciaDestino=self.cleaned_data['idFarmaciaDestino'],
                rutMotorista=self.cleaned_data['rutMotorista'],
                creado_por=autor,
                tipoMovimiento='traslado',
                producto=self.cleaned_data['producto'],
                cantidad=self.cleaned_data['cantidad'],
                prioridad=self.cleaned_data['prioridad'],
            )
            
            traslado = super().save(commit=False)
            traslado.movimiento = movimiento
            if commit:
                traslado.save()
        return traslado


class MovimientoReenvioForm(forms.ModelForm):
    """Formulario para crear un Movimiento de tipo Reenvío."""
    orden_despacho = forms.ModelChoiceField(
        queryset=OrdenDespacho.objects.filter(activo=True, estado__in=['pendiente', 'en_proceso', 'parcialmente_entregado']),
        label="Orden de Despacho",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    movimientoOriginal = forms.ModelChoiceField(
        queryset=Movimiento.objects.exclude(estado__in=['entregado', 'anulado']), 
        label="Movimiento Original a Reenviar"
    )

    class Meta:
        model = MovimientoReenvio
        fields = ['movimientoOriginal', 'motivoReenvio', 'nuevaDireccion', 'nuevaFecha', 'observaciones']
        widgets = {
            'nuevaFecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'motivoReenvio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motivo del reenvío'}),
            'nuevaDireccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nueva dirección de entrega'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones adicionales'}),
        }

    def clean_movimientoOriginal(self):
        mov_original = self.cleaned_data['movimientoOriginal']
        if mov_original.tipoMovimiento == 'reenvio':
            raise ValidationError("No se puede crear un reenvío de otro reenvío.")
        return mov_original

    def save(self, commit=True, autor=None):
        with transaction.atomic():
            movimiento_original = self.cleaned_data['movimientoOriginal']
            orden_despacho = self.cleaned_data['orden_despacho']

            # 1. Crear el nuevo movimiento base de tipo 'reenvio'
            nuevo_movimiento = Movimiento.objects.create(
                tipoMovimiento='reenvio',
                estado='pendiente',
                orden_despacho=orden_despacho,
                # Copiar datos relevantes del movimiento original
                idFarmaciaOrigen=movimiento_original.idFarmaciaOrigen,
                rutMotorista=movimiento_original.rutMotorista,
                clienteNombre=movimiento_original.clienteNombre,
                clienteTelefono=movimiento_original.clienteTelefono,
                creado_por=autor,
                metodoPago=movimiento_original.metodoPago,
                monto=movimiento_original.monto,
                producto=movimiento_original.producto,
                cantidad=movimiento_original.cantidad,
                prioridad=movimiento_original.prioridad + 1,
                # Establecer la relación con el movimiento original
                movimientoOrigen=movimiento_original,
                # Establecer la nueva dirección de destino
                direccionDestino=self.cleaned_data['nuevaDireccion'],
            )

            # 2. Crear el objeto MovimientoReenvio específico
            reenvio = super().save(commit=False)
            reenvio.movimiento = nuevo_movimiento
            if commit:
                reenvio.save()

            # 3. Actualizar el estado del movimiento original a 'fallido'
            movimiento_original.estado = 'fallido'
            movimiento_original.observaciones = (movimiento_original.observaciones or '') + f"\nReenviado con nuevo ID de movimiento: {nuevo_movimiento.idMovimiento}."
            movimiento_original.save()

        return reenvio


class CambiarEstadoMovimientoForm(forms.Form):
    """
    Formulario para cambiar el estado de un movimiento y registrarlo en la bitácora.
    """
    estado = forms.ChoiceField(
        choices=Movimiento.ESTADO_CHOICES,
        label="Nuevo Estado",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    observaciones = forms.CharField(
        label="Observaciones (Opcional)",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ej: Cliente no se encontraba en domicilio.'})
    )

    def __init__(self, *args, **kwargs):
        # Excluir el estado actual de las opciones para evitar cambios redundantes
        current_state = kwargs.pop('current_state', None)
        super().__init__(*args, **kwargs)
        if current_state:
            self.fields['estado'].choices = [choice for choice in Movimiento.ESTADO_CHOICES if choice[0] != current_state]


class ReenvioRapidoForm(forms.Form):
    """Formulario simplificado para reenvíos rápidos"""
    motivoReenvio = forms.ChoiceField(
        choices=[
            ('cliente_no_encontrado', 'Cliente no encontrado'),
            ('direccion_incorrecta', 'Dirección incorrecta'),
            ('cliente_no_responde', 'Cliente no responde'),
            ('producto_faltante', 'Producto faltante'),
            ('otro', 'Otro'),
        ],
        label="Motivo del Reenvío",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    nuevaDireccion = forms.CharField(
        label="Nueva Dirección",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nuevaFecha = forms.DateTimeField(
        label="Nueva Fecha Programada",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    observaciones = forms.CharField(
        label="Observaciones Adicionales",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def __init__(self, *args, **kwargs):
        self.movimiento_original = kwargs.pop('movimiento_original', None)
        super().__init__(*args, **kwargs)
        
        # Si hay movimiento original, pre-cargar dirección
        if self.movimiento_original and not self.initial.get('nuevaDireccion'):
            self.initial['nuevaDireccion'] = self.movimiento_original.direccionDestino

    def clean_nuevaDireccion(self):
        nueva_direccion = self.cleaned_data.get('nuevaDireccion')
        if not nueva_direccion and self.movimiento_original:
            # Si no se especifica nueva dirección, usar la original
            nueva_direccion = self.movimiento_original.direccionDestino
        return nueva_direccion
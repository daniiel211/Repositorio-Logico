from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import (
    Movimiento, MovimientoDirecto, MovimientoReceta, MovimientoTraslado, MovimientoReenvio,
    BitacoraMovimiento
)
from apps.farmacia.models import Farmacia
from apps.motorista.models import Motorista


class MovimientoBaseForm(forms.ModelForm):
    """
    Formulario base con campos comunes para la mayoría de los movimientos.
    """
    idFarmaciaOrigen = forms.ModelChoiceField(
        queryset=Farmacia.objects.filter(activo=True),
        label="Farmacia de Origen",
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    rutMotorista = forms.ModelChoiceField(
        queryset=Motorista.objects.filter(activo=True),
        label="Motorista Asignado",
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )

    class Meta:
        model = Movimiento
        fields = [
            'idFarmaciaOrigen', 'rutMotorista', 'clienteNombre', 'clienteTelefono',
            'metodoPago', 'monto', 'observaciones'
        ]
        widgets = {
            'clienteNombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
            'clienteTelefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono del cliente'}),
            'metodoPago': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is not None and monto < 0:
            raise ValidationError("El monto no puede ser negativo.")
        return monto


class MovimientoDirectoForm(MovimientoBaseForm):
    """Formulario para crear un Movimiento de tipo Directo."""
    direccionEntrega = forms.CharField(label="Dirección de Entrega", widget=forms.TextInput(attrs={'class': 'form-control'}))
    comunaEntrega = forms.CharField(label="Comuna", widget=forms.TextInput(attrs={'class': 'form-control'}))
    producto = forms.CharField(label="Producto(s)", widget=forms.TextInput(attrs={'class': 'form-control'}))
    instrucciones = forms.CharField(label="Instrucciones Adicionales", required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    class Meta(MovimientoBaseForm.Meta):
        fields = MovimientoBaseForm.Meta.fields + [
            'direccionEntrega', 'comunaEntrega', 'producto', 'instrucciones'
        ]

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
    direccionEntrega = forms.CharField(label="Dirección de Entrega", widget=forms.TextInput(attrs={'class': 'form-control'}))
    comunaEntrega = forms.CharField(label="Comuna", widget=forms.TextInput(attrs={'class': 'form-control'}))
    producto = forms.CharField(label="Producto(s)", widget=forms.TextInput(attrs={'class': 'form-control'}))
    archivoReceta = forms.FileField(label="Archivo de Receta", required=False, widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    requiereRetiroReceta = forms.BooleanField(label="Requiere retiro de receta física", required=False)

    class Meta(MovimientoBaseForm.Meta):
        fields = MovimientoBaseForm.Meta.fields + [
            'direccionEntrega', 'comunaEntrega', 'producto', 'archivoReceta', 'requiereRetiroReceta'
        ]

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
    idFarmaciaOrigen = forms.ModelChoiceField(queryset=Farmacia.objects.filter(activo=True), label="Farmacia de Origen", widget=forms.Select(attrs={'class': 'form-control select2'}))
    idFarmaciaDestino = forms.ModelChoiceField(queryset=Farmacia.objects.filter(activo=True), label="Farmacia de Destino", widget=forms.Select(attrs={'class': 'form-control select2'}))
    rutMotorista = forms.ModelChoiceField(queryset=Motorista.objects.filter(activo=True), label="Motorista", widget=forms.Select(attrs={'class': 'form-control select2'}))

    class Meta:
        model = MovimientoTraslado
        fields = ['producto', 'cantidad', 'motivoTraslado', 'observaciones']
        widgets = {
            'producto': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'motivoTraslado': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        origen = cleaned_data.get("idFarmaciaOrigen")
        destino = cleaned_data.get("idFarmaciaDestino")
        if origen and destino and origen == destino:
            raise ValidationError("La farmacia de origen y destino no pueden ser la misma.")
        return cleaned_data

    def save(self, commit=True, autor=None):
        with transaction.atomic():
            movimiento = Movimiento.objects.create(
                idFarmaciaOrigen=self.cleaned_data['idFarmaciaOrigen'],
                idFarmaciaDestino=self.cleaned_data['idFarmaciaDestino'],
                rutMotorista=self.cleaned_data['rutMotorista'],
                creado_por=autor,
                tipoMovimiento='traslado',
            )
            
            traslado = super().save(commit=False)
            traslado.movimiento = movimiento
            if commit:
                traslado.save()
        return traslado


class MovimientoReenvioForm(forms.ModelForm):
    """Formulario para crear un Movimiento de tipo Reenvío."""
    movimientoOriginal = forms.ModelChoiceField(queryset=Movimiento.objects.exclude(estado__in=['entregado', 'anulado']), label="Movimiento Original a Reenviar")

    class Meta:
        model = MovimientoReenvio
        fields = ['movimientoOriginal', 'motivoReenvio', 'nuevaDireccion', 'nuevaFecha', 'observaciones']
        widgets = {
            'nuevaFecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def clean_movimientoOriginal(self):
        mov_original = self.cleaned_data['movimientoOriginal']
        if mov_original.tipoMovimiento == 'reenvio':
            raise ValidationError("No se puede crear un reenvío de otro reenvío.")
        return mov_original

    def save(self, commit=True, autor=None):
        with transaction.atomic():
            movimiento_original = self.cleaned_data['movimientoOriginal']

            # 1. Crear el nuevo movimiento base de tipo 'reenvio'
            nuevo_movimiento = Movimiento.objects.create(
                tipoMovimiento='reenvio',
                estado='pendiente',
                # Copiar datos relevantes del movimiento original
                idFarmaciaOrigen=movimiento_original.idFarmaciaOrigen,
                rutMotorista=movimiento_original.rutMotorista,
                clienteNombre=movimiento_original.clienteNombre,
                clienteTelefono=movimiento_original.clienteTelefono,
                creado_por=autor,
                metodoPago=movimiento_original.metodoPago,
                monto=movimiento_original.monto,
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
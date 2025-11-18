"""
Formularios para la aplicación de asignaciones
Contiene formularios para crear, modificar y validar asignaciones
"""

from django import forms
from django.core.exceptions import ValidationError

# Importar modelos al inicio para evitar problemas con ModelForm
from .models import AsignacionMoto, AsignacionFarmacia
from apps.motorista.models import Motorista
from apps.moto.models import Moto
from apps.farmacia.models import Farmacia

class AsignacionMotoForm(forms.ModelForm):
    """
    Formulario para crear y editar asignaciones de moto
    Incluye validaciones y filtrado de querysets
    """
    
    class Meta:
        """
        Clase Meta para configuración del formulario
        CORRECCIÓN: Especificar el modelo directamente en Meta
        """
        model = AsignacionMoto  # CORREGIDO: Especificar modelo directamente
        fields = ['motorista', 'moto', 'observaciones']
        widgets = {
            'motorista': forms.Select(attrs={
                'class': 'form-select',
                'id': 'motorista-select'
            }),
            'moto': forms.Select(attrs={
                'class': 'form-select',
                'id': 'moto-select'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese observaciones adicionales...'
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicialización del formulario
        Solo se encarga de filtrar los querysets, no de establecer el modelo
        """
        # Llamar al constructor padre primero
        super().__init__(*args, **kwargs)
        
        # CORRECCIÓN: El modelo ya está establecido en Meta, solo filtramos querysets
        
        # Filtrar solo motoristas activos
        motoristas_asignados_ruts = AsignacionMoto.objects.filter(estado=AsignacionMoto.ESTADO_ACTIVA, activo=True).values_list('motorista__rut', flat=True)
        self.fields['motorista'].queryset = Motorista.objects.filter(activo=True).exclude(rut__in=motoristas_asignados_ruts)
        
        # Filtrar solo motos activas con documentos completos
        motos_activas = Moto.objects.filter(activo=True)
        motos_validas = [moto for moto in motos_activas if moto.documentos_completos()]
        
        # Excluir motos que ya tienen una asignación activa
        motos_asignadas = AsignacionMoto.objects.filter(estado=AsignacionMoto.ESTADO_ACTIVA, activo=True).values_list('moto_id', flat=True)
        
        # Filtrar el queryset de motos para incluir solo las válidas y no asignadas
        self.fields['moto'].queryset = Moto.objects.filter(pk__in=[moto.pk for moto in motos_validas]).exclude(pk__in=motos_asignadas)

    def clean_moto(self):
        """Valida que la moto no tenga una asignación activa."""
        moto = self.cleaned_data.get('moto')
        if moto:
            # Se excluye la instancia actual en caso de edición, usando la constante de estado
            query = AsignacionMoto.objects.filter(moto=moto, estado=AsignacionMoto.ESTADO_ACTIVA, activo=True)
            if self.instance and self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise ValidationError('Esta moto ya tiene una asignación activa y no puede ser asignada nuevamente.')
        return moto

class AsignacionFarmaciaForm(forms.ModelForm):
    """
    Formulario para crear y editar asignaciones de farmacia
    Filtra motoristas que tienen moto asignada activa
    """
    
    class Meta:
        """Configuración del formulario"""
        model = AsignacionFarmacia  # CORREGIDO: Especificar modelo directamente
        fields = ['motorista', 'farmacia', 'observaciones']
        widgets = {
            'motorista': forms.Select(attrs={
                'class': 'form-select',
                'id': 'motorista-farmacia-select'
            }),
            'farmacia': forms.Select(attrs={
                'class': 'form-select',
                'id': 'farmacia-select'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese observaciones adicionales...'
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicialización del formulario
        Filtra motoristas que tienen asignación de moto activa
        """
        # Llamar al constructor padre primero
        super().__init__(*args, **kwargs)
        
        # CORRECCIÓN: El modelo ya está establecido en Meta, solo filtramos querysets
        
        # Obtener RUTs de motoristas que tienen una moto activa asignada (consulta optimizada)
        motoristas_con_moto_activa_ruts = AsignacionMoto.objects.filter(
            estado=AsignacionMoto.ESTADO_ACTIVA, activo=True
        ).values_list('motorista__rut', flat=True)

        # Obtener RUTs de motoristas que ya tienen una farmacia activa asignada
        motoristas_con_farmacia_activa_ruts = AsignacionFarmacia.objects.filter(
            estado=AsignacionFarmacia.ESTADO_ACTIVA, activo=True
        ).values_list('motorista__rut', flat=True)
        
        # Aplicar filtros al queryset de motoristas:
        # 1. Deben estar activos.
        # 2. Deben tener una moto asignada.
        # 3. NO deben tener ya una farmacia asignada.
        self.fields['motorista'].queryset = Motorista.objects.filter(
            activo=True,
            rut__in=motoristas_con_moto_activa_ruts
        ).exclude(rut__in=motoristas_con_farmacia_activa_ruts)
        
        # Filtrar solo farmacias activas
        self.fields['farmacia'].queryset = Farmacia.objects.filter(activo=True)

    def clean_motorista(self):
        """Valida que el motorista no tenga ya una asignación de farmacia activa."""
        motorista = self.cleaned_data.get('motorista')
        if motorista and AsignacionFarmacia.objects.filter(motorista=motorista, estado=AsignacionFarmacia.ESTADO_ACTIVA, activo=True).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este motorista ya tiene una asignación de farmacia activa.')
        return motorista

class FinalizarAsignacionForm(forms.Form):
    """
    Formulario simple para finalizar asignaciones
    Solo requiere observaciones opcionales
    No es un ModelForm, por lo que no necesita modelo
    """
    
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ingrese motivo de finalización...'
        }),
        label="Observaciones de Finalización"
    )

class ReemplazarMotoristaForm(forms.Form):
    """
    Formulario para reemplazar motorista en asignación de farmacia
    Filtra motoristas disponibles para la farmacia
    No es un ModelForm, por lo que no necesita modelo
    """
    
    nuevo_motorista = forms.ModelChoiceField(
        queryset=None,  # Se establecerá en __init__
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Nuevo Motorista"
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ingrese motivo del reemplazo...'
        })
    )

    def __init__(self, farmacia_id=None, *args, **kwargs):
        """
        Inicialización del formulario
        Filtra motoristas disponibles según la farmacia
        """
        super().__init__(*args, **kwargs)
        
        if farmacia_id:
            # CORRECCIÓN: Los imports ya están al inicio del archivo
            
            # Filtrar motoristas activos con moto que no estén asignados a esta farmacia
            motoristas_con_moto = []
            for motorista in Motorista.objects.filter(activo=True):
                # Verificar si tiene moto asignada activa
                tiene_moto = AsignacionMoto.objects.filter(
                    motorista=motorista,
                    estado=AsignacionMoto.ESTADO_ACTIVA,
                    activo=True
                ).exists()
                
                # Verificar si ya tiene farmacia asignada
                tiene_farmacia = AsignacionFarmacia.objects.filter(
                    motorista=motorista,
                    estado=AsignacionFarmacia.ESTADO_ACTIVA,
                    activo=True
                ).exists()

                # Solo incluir motoristas con moto y sin farmacia asignada
                if tiene_moto and not tiene_farmacia:
                    motoristas_con_moto.append(motorista.rut)

            # Aplicar filtro al queryset
            self.fields['nuevo_motorista'].queryset = Motorista.objects.filter(
                rut__in=motoristas_con_moto
            )
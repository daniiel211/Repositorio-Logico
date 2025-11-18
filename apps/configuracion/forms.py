from django import forms
from .models import RangoAccion, TipoIncidencia, IncidenciaMovimiento, ConfiguracionSistema

class RangoAccionForm(forms.ModelForm):
    class Meta:
        model = RangoAccion
        fields = '__all__'
        widgets = {
            'comunas_permitidas': forms.Textarea(attrs={'rows': 3}),
            'horario_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'horario_fin': forms.TimeInput(attrs={'type': 'time'}),
        }

class TipoIncidenciaForm(forms.ModelForm):
    class Meta:
        model = TipoIncidencia
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class IncidenciaMovimientoForm(forms.ModelForm):
    class Meta:
        model = IncidenciaMovimiento
        fields = ['tipo_incidencia', 'descripcion', 'evidencia', 'asignada_a']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar usuarios que pueden ser asignados (supervisores y gerentes)
        self.fields['asignada_a'].queryset = self.fields['asignada_a'].queryset.filter(
            rol__in=['supervisor', 'gerente']
        )

class ConfiguracionSistemaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionSistema
        fields = ['valor', 'descripcion']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and not self.instance.editable:
            for field in self.fields:
                self.fields[field].disabled = True

class ResolverIncidenciaForm(forms.ModelForm):
    class Meta:
        model = IncidenciaMovimiento
        fields = ['resolucion']
        widgets = {
            'resolucion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describa la resolución de la incidencia...'}),
        }
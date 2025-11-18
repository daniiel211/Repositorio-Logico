from django import forms
from .models import Moto

class MotoForm(forms.ModelForm):
    class Meta:
        model = Moto
        fields = [
            'patente', 'marca', 'modelo', 'año', 'color',
            'numChasis', 'motor', 'propietario',
            'permisoCirculacion', 'seguro', 'revisionTecnica'
        ]
        widgets = {
            'patente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: AB-CD-12 o ABCD12'
            }),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'año': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1900,
                'max': 2099
            }),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'numChasis': forms.TextInput(attrs={'class': 'form-control'}),
            'motor': forms.TextInput(attrs={'class': 'form-control'}),
            'propietario': forms.Select(attrs={'class': 'form-control'}),
            'permisoCirculacion': forms.FileInput(attrs={'class': 'form-control'}),
            'seguro': forms.FileInput(attrs={'class': 'form-control'}),
            'revisionTecnica': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_patente(self):
        patente = self.cleaned_data.get('patente')
        from .models import validar_patente_chilena
        validar_patente_chilena(patente)
        return patente

class MotoSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por patente, marca o modelo...'
        })
    )
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos'), ('activas', 'Activas'), ('inactivas', 'Inactivas')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
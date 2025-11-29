from django import forms
from django.core.exceptions import ValidationError
from .models import Farmacia

class FarmaciaForm(forms.ModelForm):
    """
    Formulario de farmacia con validaciones de permisos
    """
    
    class Meta:
        model = Farmacia
        exclude = ['creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion']
        widgets = {
            'apertura': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'cierre': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese nombre de la farmacia'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese dirección completa'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +56 9 1234 5678'}),
            'IdFarmacia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID único de farmacia'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
        }

    def __init__(self, *args, **kwargs):
        # Extraer el usuario para validaciones de permisos
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Agregar class Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            # Marcar campos requeridos
            if field.required:
                field.label = f"{field.label} *"
    
    def clean(self):
        """
        Validación de permisos del usuario actual
        """
        cleaned_data = super().clean()
        
        # Validar permisos del usuario actual para crear farmacias
        if self.user and not self.user.has_perm('farmacia.add_farmacia'):
            raise ValidationError("No tiene permisos para crear farmacias")
            
        return cleaned_data
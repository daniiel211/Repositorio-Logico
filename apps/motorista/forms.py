# apps/motorista/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Motorista

class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        exclude = ['creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion']
        widgets = {
            'fechaNacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fechaUltControl': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fechaControl': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fechaVencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}),
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12.345.678-9',
                'oninput': "formatRut(this)"
            }),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidoPaterno': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidoMaterno': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'telefonoEmergencia': forms.TextInput(attrs={'class': 'form-control'}),
            'nombreContacto': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidoContacto': forms.TextInput(attrs={'class': 'form-control'}),
            'direccionContacto': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'

    def clean(self):
        """Validación de permisos del usuario actual"""
        cleaned_data = super().clean()
        
        # Validar permisos del usuario actual
        if self.user:
            if self.instance.pk:  # Edición
                if not self.user.has_perm('motorista.change_motorista'):
                    raise ValidationError("No tiene permisos para editar motoristas")
            else:  # Creación
                if not self.user.has_perm('motorista.add_motorista'):
                    raise ValidationError("No tiene permisos para crear motoristas")
                    
        return cleaned_data

    def clean_rut(self):
        """Limpia y valida el formato del RUT"""
        rut = self.cleaned_data.get('rut')
        
        if not rut:
            return rut

        rut = rut.upper().replace(".", "").replace("-", "")

        if len(rut) < 2:
            raise ValidationError("RUT demasiado corto")

        cuerpo = rut[:-1]
        dv = rut[-1]

        if not cuerpo.isdigit():
            raise ValidationError("La parte numérica del RUT debe contener solo dígitos")

        # Calcular dígito verificador
        suma = 0
        multiplo = 2

        for reverso in reversed(cuerpo):
            suma += int(reverso) * multiplo
            multiplo += 1
            if multiplo == 8:
                multiplo = 2

        resto = suma % 11
        dv_calculado = 11 - resto

        if dv_calculado == 11:
            dv_calculado = '0'
        elif dv_calculado == 10:
            dv_calculado = 'K'
        else:
            dv_calculado = str(dv_calculado)

        if dv_calculado != dv:
            raise ValidationError("El dígito verificador del RUT no es válido")

        # Formatear RUT para guardar: 12.345.678-9
        if len(cuerpo) > 6:
            rut_formateado = f"{cuerpo[:-6]}.{cuerpo[-6:-3]}.{cuerpo[-3:]}-{dv}"
        elif len(cuerpo) > 3:
            rut_formateado = f"{cuerpo[:-3]}.{cuerpo[-3:]}-{dv}"
        else:
            rut_formateado = f"{cuerpo}-{dv}"
            
        return rut_formateado
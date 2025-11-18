from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import Usuario
import re

def validar_rut_chileno(value):
    """
    Valida que el RUT tenga formato chileno válido.
    
    Args:
        value (str): RUT a validar
    
    Raises:
        ValidationError: Si el RUT no tiene formato válido
    """
    if not value:
        return
    
    # Patrón de RUT chileno: 12.345.678-9 o 12345678-9
    rut_pattern = re.compile(r'^(\d{1,3}(?:\.\d{3}){2}-[\dkK]|\d{7,8}-[\dkK])$')
    
    if not rut_pattern.match(value):
        raise ValidationError('El RUT debe tener formato chileno válido (ej: 12.345.678-9)')

class LoginForm(AuthenticationForm):
    """
    Formulario personalizado para inicio de sesión.
    Extiende AuthenticationForm de Django con estilos Bootstrap.
    """
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu nombre de usuario'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña'
        })
    )

class UsuarioCreateForm(UserCreationForm):
    """
    Formulario para creación de nuevos usuarios en el sistema.
    Incluye validaciones personalizadas y campos adicionales.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa el nombre'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa el apellido'
        })
    )
    rut = forms.CharField(
        required=False,
        max_length=15,
        validators=[validar_rut_chileno],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12.345.678-9'
        })
    )
    telefono = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56 9 1234 5678'
        })
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'rut', 'telefono', 'rol', 'password1', 'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario único'
            }),
            'rol': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'rol': 'Rol del usuario',
        }

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario y actualiza atributos de widgets"""
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })

    def clean_rut(self):
        """Limpia y valida el campo RUT"""
        rut = self.cleaned_data.get('rut')
        if rut:
            # Limpiar y formatear RUT
            rut = rut.upper().replace('.', '').replace('-', '')
            if len(rut) < 2:
                raise ValidationError('RUT demasiado corto')
        return rut

class UsuarioUpdateForm(UserChangeForm):
    """
    Formulario para actualización de usuarios existentes.
    Oculta el campo de contraseña para edición separada.
    """
    password = None  # No mostrar el campo de contraseña en la edición

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'rut', 'telefono', 'rol', 'is_active'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'is_active': 'Usuario activo',
        }

class PasswordChangeCustomForm(PasswordChangeForm):
    """
    Formulario personalizado para cambio de contraseña.
    Incluye estilos Bootstrap y placeholders descriptivos.
    """
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={ 
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={ 
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={ 
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })
    )
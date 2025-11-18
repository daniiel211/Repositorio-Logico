from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuración del administrador para el modelo Usuario personalizado.
    Extiende UserAdmin de Django para mantener funcionalidades estándar.
    """
    
    # Configuración de visualización en lista
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active', 'date_joined')
    list_filter = ('rol', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'rut')
    ordering = ('-date_joined',)
    
    # Campos para edición
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Información Personalizada LogiCo', {
            'fields': ('rut', 'telefono', 'rol')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined', 'fecha_actualizacion')
        }),
    )
    
    # Campos para creación
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'rol', 'is_active', 'is_staff'),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ('date_joined', 'last_login', 'fecha_actualizacion')

    def get_form(self, request, obj=None, **kwargs):
        """
        Personaliza el formulario para superusuarios vs usuarios normales
        """
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        
        if not is_superuser:
            # Si no es superusuario, quitar permisos avanzados
            if 'is_superuser' in form.base_fields:
                form.base_fields['is_superuser'].disabled = True
            if 'user_permissions' in form.base_fields:
                form.base_fields['user_permissions'].disabled = True
                
        return form
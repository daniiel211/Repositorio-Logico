from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario  # ✅ Importación relativa simple

class UsuarioAdmin(UserAdmin):
    """
    Configuración del administrador para el modelo Usuario personalizado.
    """
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active', 'date_joined')
    list_filter = ('rol', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'rut')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Información LogiCo', {
            'fields': ('rut', 'telefono', 'rol')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined', 'fecha_actualizacion')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'rut', 'telefono', 'rol'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined', 'fecha_actualizacion')

# Registro manual
admin.site.register(Usuario, UsuarioAdmin)
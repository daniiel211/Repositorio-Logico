# apps/motorista/admin.py
from django.contrib import admin
from .models import Motorista

@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'apellidoPaterno', 'telefono', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'comuna', 'region', 'fecha_creacion')
    search_fields = ('rut', 'nombre', 'apellidoPaterno', 'apellidoMaterno')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        else:
            obj.modificado_por = request.user
        super().save_model(request, obj, form, change)
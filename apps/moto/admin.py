from django.contrib import admin
from .models import Moto

@admin.register(Moto)
class MotoAdmin(admin.ModelAdmin):
    list_display = [
        'patente', 'marca', 'modelo', 'año', 'color', 
        'propietario', 'activo', 'fecha_creacion'
    ]
    list_filter = ['activo', 'propietario', 'marca', 'año']
    search_fields = ['patente', 'marca', 'modelo', 'numChasis', 'motor']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    list_per_page = 20
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'patente', 'marca', 'modelo', 'año', 'color',
                'numChasis', 'motor', 'propietario'
            )
        }),
        ('Documentos', {
            'fields': ('permisoCirculacion', 'seguro', 'revisionTecnica')
        }),
        ('Auditoría', {
            'fields': (
                'activo', 'creado_por', 'fecha_creacion',
                'modificado_por', 'fecha_modificacion'
            )
        }),
    )
from django.contrib import admin
from .models import RangoAccion, TipoIncidencia, IncidenciaMovimiento, ConfiguracionSistema

@admin.register(RangoAccion)
class RangoAccionAdmin(admin.ModelAdmin):
    list_display = ['farmacia', 'distancia_maxima_km', 'horario_operacion', 'activo']
    list_filter = ['activo', 'farmacia__comuna']
    search_fields = ['farmacia__nombre', 'farmacia__idFarmacia']
    raw_id_fields = ['farmacia', 'creado_por', 'modificado_por']

@admin.register(TipoIncidencia)
class TipoIncidenciaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'gravedad', 'requiere_autorizacion', 'activo']
    list_filter = ['gravedad', 'requiere_autorizacion', 'activo']
    search_fields = ['codigo', 'nombre', 'descripcion']

@admin.register(IncidenciaMovimiento)
class IncidenciaMovimientoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'movimiento', 
        'tipo_incidencia', 
        'estado', 
        'fecha_incidencia',
        'reportada_por'
    ]
    list_filter = ['estado', 'tipo_incidencia', 'fecha_incidencia']
    search_fields = [
        'movimiento__idMovimiento',
        'descripcion',
        'reportada_por__username'
    ]
    raw_id_fields = [
        'movimiento', 
        'tipo_incidencia',
        'reportada_por',
        'asignada_a',
        'resuelta_por'
    ]
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'movimiento', 'tipo_incidencia', 'reportada_por'
        )

@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ['clave', 'valor', 'tipo', 'editable', 'fecha_modificacion']
    list_filter = ['tipo', 'editable']
    search_fields = ['clave', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    
    def get_readonly_fields(self, request, obj=None):
        if obj and not obj.editable:
            return ['clave', 'tipo', 'editable', 'fecha_creacion', 'fecha_modificacion']
        return self.readonly_fields
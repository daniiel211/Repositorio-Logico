from django.contrib import admin
from .models import AsignacionMoto, AsignacionFarmacia

@admin.register(AsignacionMoto)
class AsignacionMotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'motorista', 'moto', 'estado', 'fecha_asignacion', 'fecha_finalizacion', 'activo']
    list_filter = ['estado', 'activo', 'fecha_asignacion']
    search_fields = ['motorista__rut', 'motorista__nombre', 'moto__patente', 'moto__marca']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    list_editable = ['estado']
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('motorista', 'moto', 'estado', 'observaciones')
        }),
        ('Fechas', {
            'fields': ('fecha_asignacion', 'fecha_finalizacion')
        }),
        ('Auditoría', {
            'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')
        }),
    )

@admin.register(AsignacionFarmacia)
class AsignacionFarmaciaAdmin(admin.ModelAdmin):
    list_display = ['id', 'motorista', 'farmacia', 'estado', 'fecha_asignacion', 'fecha_finalizacion', 'activo']
    list_filter = ['estado', 'activo', 'fecha_asignacion', 'farmacia']
    search_fields = ['motorista__rut', 'motorista__nombre', 'farmacia__IdFarmacia', 'farmacia__nombre']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    list_editable = ['estado']
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('motorista', 'farmacia', 'estado', 'observaciones')
        }),
        ('Fechas', {
            'fields': ('fecha_asignacion', 'fecha_finalizacion')
        }),
        ('Auditoría', {
            'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')
        }),
    )
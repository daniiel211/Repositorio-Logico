from django.contrib import admin
from .models import ConfiguracionReporte, ReporteGenerado

@admin.register(ConfiguracionReporte)
class ConfiguracionReporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_reporte', 'formato_salida', 'activo', 'fecha_creacion')
    list_filter = ('tipo_reporte', 'formato_salida', 'activo')
    search_fields = ('nombre',)

@admin.register(ReporteGenerado)
class ReporteGeneradoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo_reporte', 'formato', 'fecha_generacion', 'estado')
    list_filter = ('tipo_reporte', 'formato', 'estado', 'fecha_generacion')
    search_fields = ('usuario__username', 'nombre_archivo')
    readonly_fields = ('fecha_generacion',)
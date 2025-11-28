from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.db.models import Count, Q

def home(request):
    """Página de inicio pública - Acceso libre"""
    context = {
        'titulo': 'Sistema de Gestión Logística',
        'descripcion': 'Automatiza los procesos de despacho a domicilio'
    }
    return render(request, 'core/home.html', context)

def acerca(request):
    """Página acerca del sistema - Acceso libre"""
    context = {
        'titulo': 'Acerca de LogiCo',
    }
    return render(request, 'core/acerca.html', context)

@login_required
@permission_required('core.view_estadisticas', raise_exception=True)
def estadisticas_avanzadas(request):
    """
    Página para mostrar estadísticas avanzadas
    Requiere permiso: core.view_estadisticas
    """
    context = {'titulo': 'Estadísticas Avanzadas'}
    return render(request, 'core/estadisticas.html', context)

# Vistas basadas en clases con mixins de permisos
class DashboardView(PermissionRequiredMixin, TemplateView):
    """
    Dashboard principal del sistema
    Requiere permiso: core.view_dashboard
    """
    template_name = 'core/dashboard.html'
    permission_required = 'core.view_dashboard'
    raise_exception = True
    login_url = '/acceso-denegado/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Dashboard Principal'
        
        # Cargar datos para el dashboard
        try:
            from apps.farmacia.models import Farmacia
            from apps.motorista.models import Motorista
            from apps.moto.models import Moto
            from apps.asignacion.models import AsignacionMoto, AsignacionFarmacia
            
            # Estadísticas básicas
            context['total_farmacias'] = Farmacia.objects.filter(estado='activo').count()
            context['total_motoristas'] = Motorista.objects.filter(estado='activo').count()
            context['total_motos'] = Moto.objects.filter(estado='activo').count()
            context['asignaciones_moto_activas'] = AsignacionMoto.objects.filter(estado='activo').count()
            context['asignaciones_farmacia_activas'] = AsignacionFarmacia.objects.filter(estado='activo').count()
            
            # Estadísticas adicionales
            context['motoristas_con_moto'] = AsignacionMoto.objects.filter(
                estado='activo'
            ).values('motorista').distinct().count()
            
            context['motoristas_con_farmacia'] = AsignacionFarmacia.objects.filter(
                estado='activo'
            ).values('motorista').distinct().count()
            
            # Últimas asignaciones (ejemplo)
            context['ultimas_asignaciones_moto'] = AsignacionMoto.objects.filter(
                estado='activo'
            ).select_related('motorista', 'moto')[:5]
            
            context['ultimas_asignaciones_farmacia'] = AsignacionFarmacia.objects.filter(
                estado='activo'
            ).select_related('motorista', 'farmacia')[:5]
            
            # Farmacias top (ejemplo)
            context['farmacias_top'] = Farmacia.objects.filter(
                estado='activo'
            ).annotate(
                num_motoristas=Count('asignacionfarmacia')
            ).order_by('-num_motoristas')[:3]
            
        except Exception as e:
            context['error'] = str(e)
            # Valores por defecto en caso de error
            context.update({
                'total_farmacias': 0,
                'total_motoristas': 0,
                'total_motos': 0,
                'asignaciones_moto_activas': 0,
                'asignaciones_farmacia_activas': 0,
                'motoristas_con_moto': 0,
                'motoristas_con_farmacia': 0,
                'ultimas_asignaciones_moto': [],
                'ultimas_asignaciones_farmacia': [],
                'farmacias_top': [],
            })
        
        return context

class ConfiguracionSistemaView(PermissionRequiredMixin, TemplateView):
    """
    Vista de configuración del sistema
    Solo accesible para gerentes
    """
    template_name = 'core/configuracion_sistema.html'
    permission_required = 'core.change_configuracionsistema'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Configuración del Sistema'
        return context
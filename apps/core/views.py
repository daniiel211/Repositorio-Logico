# apps/core/views.py - ARCHIVO COMPLETO

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

# VISTAS PÚBLICAS

def home(request):
    """
    Página de inicio pública - Accesible sin autenticación
    """
    return render(request, 'core/home.html', {
        'nombre_sistema': 'LogiCo',
        'version_sistema': '1.0.0',
        'empresa_cliente': 'Discopro Ltda.',
        'cliente_final': 'Cruz Verde',
    })

def acerca(request):
    """
    Página "Acerca de" - Accesible sin autenticación
    """
    return render(request, 'core/acerca.html', {
        'nombre_sistema': 'LogiCo',
        'version_sistema': '1.0.0',
        'descripcion': 'Sistema de gestión logística para farmacias Cruz Verde',
    })

# VISTAS PROTEGIDAS (requieren autenticación)

class DashboardView(TemplateView):
    """
    Vista del Dashboard Principal - Accesible para TODOS los usuarios autenticados
    """
    template_name = 'core/dashboard.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Contexto básico para todos los usuarios
        context['nombre_sistema'] = 'LogiCo'
        context['version_sistema'] = '1.0.0'
        context['usuario'] = user
        context['rol_usuario'] = user.get_rol_display() if hasattr(user, 'get_rol_display') else 'Usuario'
        
        # Estadísticas específicas por rol (opcional)
        if hasattr(user, 'es_gerente') and (user.es_gerente or user.is_superuser):
            try:
                from apps.farmacia.models import Farmacia
                from apps.motorista.models import Motorista
                from apps.moto.models import Moto
                from apps.usuario.models import Usuario
                
                context['total_farmacias'] = Farmacia.objects.count()
                context['total_motoristas'] = Motorista.objects.count()
                context['total_motos'] = Moto.objects.count()
                context['total_usuarios'] = Usuario.objects.filter(is_active=True).count()
                context['rol_usuario'] = 'Gerente'
            except ImportError:
                # Si los modelos no existen aún, usar valores por defecto
                pass
            
        return context

class ConfiguracionSistemaView(TemplateView):
    """
    Vista de Configuración del Sistema - Solo para gerentes
    """
    template_name = 'core/configuracion_sistema.html'
    
    @method_decorator(login_required)
    @method_decorator(permission_required('core.change_configuracionsistema', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_sistema'] = 'LogiCo'
        context['configuraciones'] = [
            {'nombre': 'Tiempo máximo de entrega', 'valor': '60 minutos', 'descripcion': 'Tiempo máximo para completar una entrega'},
            {'nombre': 'Radio de cobertura', 'valor': '10 km', 'descripcion': 'Distancia máxima para asignaciones'},
            {'nombre': 'Horario de operación', 'valor': '08:00 - 22:00', 'descripcion': 'Horario de atención del sistema'},
        ]
        return context

@login_required
@permission_required('core.view_estadisticas', raise_exception=True)
def estadisticas(request):
    """
    Vista de Estadísticas Avanzadas - Requiere permiso específico
    """
    return render(request, 'core/estadisticas.html', {
        'nombre_sistema': 'LogiCo',
        'titulo': 'Estadísticas Avanzadas',
    })

# Vista alternativa de dashboard basada en función
@login_required
def dashboard_simple(request):
    """
    Dashboard simple - alternativa funcional
    """
    user = request.user
    context = {
        'nombre_sistema': 'LogiCo',
        'version_sistema': '1.0.0',
        'usuario': user,
        'rol_usuario': user.get_rol_display() if hasattr(user, 'get_rol_display') else 'Usuario',
    }
    
    # Agregar estadísticas si es gerente
    if hasattr(user, 'es_gerente') and (user.es_gerente or user.is_superuser):
        try:
            from apps.farmacia.models import Farmacia
            from apps.motorista.models import Motorista
            
            context['total_farmacias'] = Farmacia.objects.count()
            context['total_motoristas'] = Motorista.objects.count()
        except ImportError:
            pass
    
    return render(request, 'core/dashboard.html', context)
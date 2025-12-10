# apps/core/views.py - ARCHIVO COMPLETO ACTUALIZADO
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse

# Importar decoradores personalizados
from apps.usuario.decorators import require_roles

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
        
        # Manejar el rol del usuario
        if hasattr(user, 'get_rol_display'):
            context['rol_usuario'] = user.get_rol_display()
        elif hasattr(user, 'rol'):
            context['rol_usuario'] = user.rol.title()
        else:
            context['rol_usuario'] = 'Usuario'
        
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
                context['es_gerente'] = True
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
    @method_decorator(require_roles(['gerente']))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_sistema'] = 'LogiCo'
        
        try:
            from apps.configuracion.models import ConfiguracionSistema
            configuraciones = ConfiguracionSistema.objects.all()
            context['configuraciones'] = [
                {
                    'nombre': config.clave,
                    'valor': config.valor,
                    'descripcion': config.descripcion,
                    'tipo': config.tipo
                }
                for config in configuraciones
            ]
        except:
            # Configuraciones por defecto si el modelo no existe
            context['configuraciones'] = [
                {'nombre': 'Tiempo máximo de entrega', 'valor': '60 minutos', 'descripcion': 'Tiempo máximo para completar una entrega', 'tipo': 'NUMERO'},
                {'nombre': 'Radio de cobertura', 'valor': '10 km', 'descripcion': 'Distancia máxima para asignaciones', 'tipo': 'NUMERO'},
                {'nombre': 'Horario de operación', 'valor': '08:00 - 22:00', 'descripcion': 'Horario de atención del sistema', 'tipo': 'TEXTO'},
            ]
        
        return context

@login_required
@require_roles(['gerente', 'supervisor'])
def estadisticas(request):
    """
    Vista de Estadísticas Avanzadas - Solo para gerentes y supervisores
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
    }
    
    # Manejar el rol del usuario
    if hasattr(user, 'get_rol_display'):
        context['rol_usuario'] = user.get_rol_display()
    elif hasattr(user, 'rol'):
        context['rol_usuario'] = user.rol.title()
    else:
        context['rol_usuario'] = 'Usuario'
    
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
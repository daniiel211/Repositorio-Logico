from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

def home(request):
    """Página de inicio pública"""
    context = {
        'titulo': 'Sistema de Gestión Logística',
        'descripcion': 'Automatiza los procesos de despacho a domicilio'
    }
    return render(request, 'core/home.html', context)

def acerca(request):
    """Página acerca del sistema"""
    context = {
        'titulo': 'Acerca de LogiCo',
    }
    return render(request, 'core/acerca.html', context)

@login_required
def estadisticas_avanzadas(request):
    """Página para mostrar estadísticas avanzadas"""
    context = {'titulo': 'Estadísticas Avanzadas'}
    return render(request, 'core/estadisticas.html', context)
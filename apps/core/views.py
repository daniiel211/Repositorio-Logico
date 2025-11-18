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

@login_required
def dashboard(request):
    """
    Dashboard principal del sistema.
    Redirige al usuario a su dashboard correspondiente según su rol.
    """
    # Asumimos que tu modelo de usuario (request.user) tiene un campo 'rol'.
    # Ajusta 'Operador' si el valor en tu base de datos es diferente.
    if hasattr(request.user, 'rol') and request.user.rol == 'Operador':
        # Si es Operador, muestra el dashboard de operador.
        return render(request, 'usuario/dashboard_operador.html')

    try:
        # Importar aquí para evitar dependencias circulares
        from apps.farmacia.models import Farmacia
        from apps.motorista.models import Motorista
        from apps.moto.models import Moto
        from apps.asignacion.models import AsignacionMoto, AsignacionFarmacia
        
        # Métricas básicas
        total_farmacias = Farmacia.objects.filter(activo=True).count()
        total_motoristas = Motorista.objects.filter(activo=True).count()
        total_motos = Moto.objects.filter(activo=True).count()
        
        # Asignaciones activas del nuevo módulo
        asignaciones_moto_activas = AsignacionMoto.objects.filter(
            estado='ACTIVA', 
            activo=True
        ).count()
        
        asignaciones_farmacia_activas = AsignacionFarmacia.objects.filter(
            estado='ACTIVA', 
            activo=True
        ).count()
        
        # Estadísticas adicionales
        motoristas_con_moto = 0
        for motorista in Motorista.objects.filter(activo=True):
            if AsignacionMoto.objects.filter(
                motorista=motorista, 
                estado='ACTIVA', 
                activo=True
            ).exists():
                motoristas_con_moto += 1
        
        motoristas_con_farmacia = 0
        for motorista in Motorista.objects.filter(activo=True):
            if AsignacionFarmacia.objects.filter(
                motorista=motorista, 
                estado='ACTIVA', 
                activo=True
            ).exists():
                motoristas_con_farmacia += 1
        
        # Últimas asignaciones de motos
        ultimas_asignaciones_moto = AsignacionMoto.objects.filter(
            activo=True
        ).select_related('motorista', 'moto').order_by('-fecha_creacion')[:5]
        
        # Últimas asignaciones de farmacias
        ultimas_asignaciones_farmacia = AsignacionFarmacia.objects.filter(
            activo=True
        ).select_related('motorista', 'farmacia').order_by('-fecha_creacion')[:5]
        
        context = {
            'titulo': 'Dashboard Principal',
            'total_farmacias': total_farmacias,
            'total_motoristas': total_motoristas,
            'total_motos': total_motos,
            'asignaciones_moto_activas': asignaciones_moto_activas,
            'asignaciones_farmacia_activas': asignaciones_farmacia_activas,
            'motoristas_con_moto': motoristas_con_moto,
            'motoristas_con_farmacia': motoristas_con_farmacia,
            'ultimas_asignaciones_moto': ultimas_asignaciones_moto,
            'ultimas_asignaciones_farmacia': ultimas_asignaciones_farmacia,
        }
        
    except Exception as e:
        # En caso de error (por ejemplo, tablas no creadas aún)
        context = {
            'titulo': 'Dashboard Principal',
            'total_farmacias': 0,
            'total_motoristas': 0,
            'total_motos': 0,
            'asignaciones_moto_activas': 0,
            'asignaciones_farmacia_activas': 0,
            'motoristas_con_moto': 0,
            'motoristas_con_farmacia': 0,
            'ultimas_asignaciones_moto': [],
            'ultimas_asignaciones_farmacia': [],
            'error': str(e)
        }
    
    return render(request, 'core/dashboard.html', context)

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
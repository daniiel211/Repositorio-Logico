from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

from .models import RangoAccion, TipoIncidencia, IncidenciaMovimiento, ConfiguracionSistema
from .forms import IncidenciaMovimientoForm, ResolverIncidenciaForm

def check_rol_supervisor(user):
    """Verifica si el usuario tiene rol de supervisor o gerente"""
    return user.rol in ['supervisor', 'gerente']

def check_rol_gerente(user):
    """Verifica si el usuario es gerente"""
    return user.rol == 'gerente'

@login_required
def dashboard_configuracion(request):
    """Dashboard principal de configuración"""
    context = {
        'total_incidencias_abiertas': IncidenciaMovimiento.objects.filter(
            estado__in=['REGISTRADA', 'EN_REVISION', 'ESCALADA']
        ).count(),
        'total_rangos_configurados': RangoAccion.objects.filter(activo=True).count(),
    }
    
    if request.user.rol in ['supervisor', 'gerente']:
        context['incidencias_pendientes'] = IncidenciaMovimiento.objects.filter(
            estado__in=['REGISTRADA', 'EN_REVISION']
        ).select_related('movimiento', 'tipo_incidencia', 'reportada_por')[:10]
    
    return render(request, 'configuracion/dashboard.html', context)

@login_required
def lista_incidencias(request):
    """Lista de incidencias con filtros"""
    incidencias = IncidenciaMovimiento.objects.all().select_related(
        'movimiento', 'tipo_incidencia', 'reportada_por', 'asignada_a'
    )
    
    # Filtros
    estado = request.GET.get('estado')
    tipo = request.GET.get('tipo')
    
    if estado:
        incidencias = incidencias.filter(estado=estado)
    if tipo:
        incidencias = incidencias.filter(tipo_incidencia__codigo=tipo)
    
    # Motoristas solo ven sus propias incidencias
    if request.user.rol == 'motorista':
        incidencias = incidencias.filter(movimiento__rutMotorista__rut=request.user.rut)
    
    context = {
        'incidencias': incidencias,
        'tipos_incidencia': TipoIncidencia.objects.filter(activo=True),
    }
    return render(request, 'configuracion/lista_incidencias.html', context)

@login_required
def detalle_incidencia(request, incidencia_id):
    """Detalle de una incidencia específica"""
    incidencia = get_object_or_404(
        IncidenciaMovimiento.objects.select_related(
            'movimiento',
            'tipo_incidencia',
            'reportada_por',
            'asignada_a',
            'resuelta_por'
        ),
        id=incidencia_id
    )
    
    # Verificar permisos
    if (request.user.rol == 'motorista' and 
        incidencia.movimiento.rutMotorista.rut != request.user.rut):
        messages.error(request, 'No tiene permisos para ver esta incidencia.')
        return redirect('configuracion:lista_incidencias')
    
    form = None
    if request.user.rol in ['supervisor', 'gerente'] and incidencia.estado != 'RESUELTA':
        form = ResolverIncidenciaForm(instance=incidencia)
    
    context = {
        'incidencia': incidencia,
        'form': form,
    }
    return render(request, 'configuracion/detalle_incidencia.html', context)

@login_required
def reportar_incidencia(request, movimiento_id=None):
    """Reportar una nueva incidencia"""
    from apps.movimiento.models import Movimiento
    
    movimiento = None
    if movimiento_id:
        movimiento = get_object_or_404(Movimiento, idMovimiento=movimiento_id)
    
    if request.method == 'POST':
        form = IncidenciaMovimientoForm(request.POST, request.FILES)
        if form.is_valid():
            incidencia = form.save(commit=False)
            if movimiento:
                incidencia.movimiento = movimiento
            incidencia.reportada_por = request.user
            incidencia.save()
            
            messages.success(request, 'Incidencia reportada correctamente.')
            return redirect('configuracion:detalle_incidencia', incidencia_id=incidencia.id)
    else:
        form = IncidenciaMovimientoForm(initial={'movimiento': movimiento} if movimiento else None)
    
    context = {
        'form': form,
        'movimiento': movimiento,
        'tipos_incidencia': TipoIncidencia.objects.filter(activo=True),
    }
    return render(request, 'configuracion/reportar_incidencia.html', context)

@login_required
@user_passes_test(check_rol_supervisor)
def resolver_incidencia(request, incidencia_id):
    """Resolver una incidencia (solo supervisores y gerentes)"""
    incidencia = get_object_or_404(IncidenciaMovimiento, id=incidencia_id)
    
    if request.method == 'POST':
        form = ResolverIncidenciaForm(request.POST, instance=incidencia)
        if form.is_valid():
            incidencia = form.save(commit=False)
            incidencia.marcar_como_resuelta(request.user, form.cleaned_data['resolucion'])
            messages.success(request, 'Incidencia marcada como resuelta.')
            return redirect('configuracion:detalle_incidencia', incidencia_id=incidencia.id)
    else:
        form = ResolverIncidenciaForm(instance=incidencia)
    
    context = {
        'incidencia': incidencia,
        'form': form,
    }
    return render(request, 'configuracion/resolver_incidencia.html', context)

@login_required
@user_passes_test(check_rol_gerente)
def gestion_rangos_accion(request):
    """Gestión de rangos de acción (solo gerente)"""
    rangos = RangoAccion.objects.select_related('farmacia', 'creado_por').all()
    
    context = {
        'rangos': rangos,
    }
    return render(request, 'configuracion/gestion_rangos.html', context)

@login_required
def api_verificar_rango(request, farmacia_id, lat, lng):
    """API para verificar si una coordenada está dentro del rango de acción"""
    from farmacia.models import Farmacia
    from django.contrib.gis.geos import Point
    from django.contrib.gis.db.models.functions import Distance
    from django.contrib.gis.measure import D
    
    try:
        farmacia = Farmacia.objects.get(idFarmacia=farmacia_id)
        rango = RangoAccion.objects.get(farmacia=farmacia)
        
        punto_destino = Point(float(lng), float(lat))
        punto_farmacia = Point(float(farmacia.longitud), float(farmacia.latitud))
        
        distancia_km = punto_farmacia.distance(punto_destino) * 100  # Aproximación a km
        
        dentro_rango = distancia_km <= float(rango.distancia_maxima_km)
        
        return JsonResponse({
            'dentro_rango': dentro_rango,
            'distancia_calculada': round(distancia_km, 2),
            'distancia_maxima': float(rango.distancia_maxima_km),
            'requiere_autorizacion': not dentro_rango
        })
    except (Farmacia.DoesNotExist, RangoAccion.DoesNotExist):
        return JsonResponse({'error': 'Farmacia o rango no configurado'}, status=404)

@login_required
@user_passes_test(check_rol_gerente)
def gestion_rangos(request):
    """Gestión de rangos de acción (solo gerente)"""
    from apps.farmacia.models import Farmacia
    from .models import RangoAccion
    
    rangos = RangoAccion.objects.select_related('farmacia', 'creado_por', 'modificado_por').all()
    
    # Contar farmacias sin configuración
    farmacias_con_rango = [rango.farmacia_id for rango in rangos]
    farmacias_sin_configurar = Farmacia.objects.filter(activo=True).exclude(
        IdFarmacia__in=farmacias_con_rango
    ).count()
    
    context = {
        'rangos': rangos,
        'farmacias_sin_configurar': farmacias_sin_configurar,
    }
    return render(request, 'configuracion/gestion_rangos.html', context)

@login_required
def reportar_incidencia(request, movimiento_id=None):
    """Reportar una nueva incidencia"""
    from apps.movimiento.models import Movimiento
    from .models import TipoIncidencia
    
    movimiento = None
    if movimiento_id:
        movimiento = get_object_or_404(Movimiento, idMovimiento=movimiento_id)
    
    if request.method == 'POST':
        form = IncidenciaMovimientoForm(request.POST, request.FILES)
        if form.is_valid():
            incidencia = form.save(commit=False)
            if movimiento:
                incidencia.movimiento = movimiento
            incidencia.reportada_por = request.user
            incidencia.save()
            
            messages.success(request, 'Incidencia reportada correctamente.')
            return redirect('configuracion:detalle_incidencia', incidencia_id=incidencia.id)
    else:
        form = IncidenciaMovimientoForm(initial={'movimiento': movimiento} if movimiento else None)
    
    context = {
        'form': form,
        'movimiento': movimiento,
        'tipos_incidencia': TipoIncidencia.objects.filter(activo=True),
    }
    return render(request, 'configuracion/reportar_incidencia.html', context)
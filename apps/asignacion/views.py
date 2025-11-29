# apps/asignacion/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from .models import AsignacionMoto, AsignacionFarmacia
from .forms import (
    AsignacionMotoForm,
    AsignacionFarmaciaForm,
    FinalizarAsignacionForm,
    ReemplazarMotoristaForm
)

# Permisos para asignaciones de moto
@login_required
@permission_required('asignacion.view_asignacionmoto', raise_exception=True)
def dashboard_asignaciones(request):
    """Dashboard principal de asignaciones"""
    # Importar aquí para evitar dependencias circulares
    from apps.motorista.models import Motorista
    from apps.moto.models import Moto
    from apps.farmacia.models import Farmacia
    
    # Estadísticas
    total_motoristas_activos = Motorista.objects.filter(activo=True).count()
    total_motos_activas = Moto.objects.filter(activo=True).count()
    total_farmacias_activas = Farmacia.objects.filter(activo=True).count()
    
    asignaciones_moto_activas = AsignacionMoto.objects.filter(estado='ACTIVA', activo=True).count()
    asignaciones_farmacia_activas = AsignacionFarmacia.objects.filter(estado='ACTIVA', activo=True).count()
    
    # Últimas asignaciones
    ultimas_asignaciones_moto = AsignacionMoto.objects.filter(activo=True).order_by('-fecha_creacion')[:5]
    ultimas_asignaciones_farmacia = AsignacionFarmacia.objects.filter(activo=True).order_by('-fecha_creacion')[:5]
    
    context = {
        'total_motoristas_activos': total_motoristas_activos,
        'total_motos_activas': total_motos_activas,
        'total_farmacias_activas': total_farmacias_activas,
        'asignaciones_moto_activas': asignaciones_moto_activas,
        'asignaciones_farmacia_activas': asignaciones_farmacia_activas,
        'ultimas_asignaciones_moto': ultimas_asignaciones_moto,
        'ultimas_asignaciones_farmacia': ultimas_asignaciones_farmacia,
    }
    
    return render(request, 'asignacion/dashboard.html', context)

@login_required
@permission_required('asignacion.view_asignacionmoto', raise_exception=True)
def listar_asignaciones_moto(request):
    """Lista todas las asignaciones de motos con filtros"""
    asignaciones = AsignacionMoto.objects.filter(activo=True).order_by('-fecha_asignacion')
    
    # Filtros
    estado = request.GET.get('estado')
    motorista = request.GET.get('motorista')
    moto = request.GET.get('moto')
    
    if estado:
        asignaciones = asignaciones.filter(estado=estado)
    if motorista:
        asignaciones = asignaciones.filter(motorista__rut__icontains=motorista)
    if moto:
        asignaciones = asignaciones.filter(moto__patente__icontains=moto)
    
    context = {
        'asignaciones': asignaciones,
        'estados': AsignacionMoto.ESTADOS_ASIGNACION,
    }
    
    return render(request, 'asignacion/listar_motos.html', context)

@login_required
@permission_required('asignacion.add_asignacionmoto', raise_exception=True)
def crear_asignacion_moto(request):
    """Crea una nueva asignación de moto"""
    if request.method == 'POST':
        form = AsignacionMotoForm(request.POST)
        if form.is_valid():
            asignacion = form.save(commit=False)
            asignacion.creado_por = request.user
            asignacion.save()
            messages.success(request, 'Asignación de moto creada exitosamente.')
            return redirect('asignacion:listar_motos')
    else:
        form = AsignacionMotoForm()
    
    context = {
        'form': form,
        'titulo': 'Asignar Moto a Motorista'
    }
    
    return render(request, 'asignacion/form_asignacion.html', context)

@login_required
@permission_required('asignacion.change_asignacionmoto', raise_exception=True)
def finalizar_asignacion_moto(request, id):
    """Finaliza una asignación de moto"""
    asignacion = get_object_or_404(AsignacionMoto, id=id, activo=True)
    
    if request.method == 'POST':
        form = FinalizarAsignacionForm(request.POST)
        if form.is_valid():
            observaciones = form.cleaned_data['observaciones']
            if observaciones:
                if asignacion.observaciones:
                    asignacion.observaciones += f"\n--- FINALIZACIÓN ---\n{observaciones}"
                else:
                    asignacion.observaciones = f"--- FINALIZACIÓN ---\n{observaciones}"
            asignacion.finalizar(request.user)
            messages.success(request, 'Asignación de moto finalizada exitosamente.')
            return redirect('asignacion:listar_motos')
    else:
        form = FinalizarAsignacionForm()
    
    context = {
        'form': form,
        'asignacion': asignacion,
        'titulo': 'Finalizar Asignación de Moto',
        'tipo_asignacion': 'moto'
    }
    
    return render(request, 'asignacion/finalizar_asignacion.html', context)

@login_required
@permission_required('asignacion.view_asignacionmoto', raise_exception=True)
def detalle_asignacion_moto(request, id):
    """Muestra el detalle de una asignación de moto"""
    asignacion = get_object_or_404(AsignacionMoto, id=id, activo=True)
    context = {
        'asignacion': asignacion,
        'titulo': 'Detalle Asignación de Moto'
    }
    return render(request, 'asignacion/detalle_moto.html', context)

# Permisos para asignaciones de farmacia
@login_required
@permission_required('asignacion.view_asignacionfarmacia', raise_exception=True)
def listar_asignaciones_farmacia(request):
    """Lista todas las asignaciones de farmacias con filtros"""
    asignaciones = AsignacionFarmacia.objects.filter(activo=True).order_by('-fecha_asignacion')
    
    # Filtros
    estado = request.GET.get('estado')
    motorista = request.GET.get('motorista')
    farmacia = request.GET.get('farmacia')
    
    if estado:
        asignaciones = asignaciones.filter(estado=estado)
    if motorista:
        asignaciones = asignaciones.filter(motorista__rut__icontains=motorista)
    if farmacia:
        asignaciones = asignaciones.filter(farmacia__IdFarmacia__icontains=farmacia)
    
    context = {
        'asignaciones': asignaciones,
        'estados': AsignacionFarmacia.ESTADOS_ASIGNACION,
    }
    
    return render(request, 'asignacion/listar_farmacias.html', context)

@login_required
@permission_required('asignacion.add_asignacionfarmacia', raise_exception=True)
def crear_asignacion_farmacia(request):
    """Crea una nueva asignación de farmacia"""
    if request.method == 'POST':
        form = AsignacionFarmaciaForm(request.POST)
        if form.is_valid():
            asignacion = form.save(commit=False)
            asignacion.creado_por = request.user
            asignacion.save()
            messages.success(request, 'Asignación de farmacia creada exitosamente.')
            return redirect('asignacion:listar_farmacias')
    else:
        form = AsignacionFarmaciaForm()
    
    context = {
        'form': form,
        'titulo': 'Asignar Motorista a Farmacia'
    }
    
    return render(request, 'asignacion/form_asignacion.html', context)

@login_required
@permission_required('asignacion.change_asignacionfarmacia', raise_exception=True)
def finalizar_asignacion_farmacia(request, id):
    """Finaliza una asignación de farmacia"""
    asignacion = get_object_or_404(AsignacionFarmacia, id=id, activo=True)
    
    if request.method == 'POST':
        form = FinalizarAsignacionForm(request.POST)
        if form.is_valid():
            observaciones = form.cleaned_data['observaciones']
            if observaciones:
                if asignacion.observaciones:
                    asignacion.observaciones += f"\n--- FINALIZACIÓN ---\n{observaciones}"
                else:
                    asignacion.observaciones = f"--- FINALIZACIÓN ---\n{observaciones}"
            asignacion.finalizar(request.user)
            messages.success(request, 'Asignación de farmacia finalizada exitosamente.')
            return redirect('asignacion:listar_farmacias')
    else:
        form = FinalizarAsignacionForm()
    
    context = {
        'form': form,
        'asignacion': asignacion,
        'titulo': 'Finalizar Asignación de Farmacia',
        'tipo_asignacion': 'farmacia'
    }
    
    return render(request, 'asignacion/finalizar_asignacion.html', context)

@login_required
@permission_required('asignacion.change_asignacionfarmacia', raise_exception=True)
def reemplazar_motorista(request, farmacia_id):
    """Reemplaza un motorista en una farmacia"""
    from apps.farmacia.models import Farmacia
    
    farmacia = get_object_or_404(Farmacia, IdFarmacia=farmacia_id, activo=True)
    asignacion_actual = get_object_or_404(
        AsignacionFarmacia,
        farmacia=farmacia,
        estado='ACTIVA',
        activo=True
    )
    
    if request.method == 'POST':
        form = ReemplazarMotoristaForm(farmacia_id, request.POST)
        if form.is_valid():
            nuevo_motorista = form.cleaned_data['nuevo_motorista']
            observaciones = form.cleaned_data['observaciones']
            
            # Finalizar asignación actual
            if observaciones:
                if asignacion_actual.observaciones:
                    asignacion_actual.observaciones += f"\n--- REEMPLAZO ---\n{observaciones}"
                else:
                    asignacion_actual.observaciones = f"--- REEMPLAZO ---\n{observaciones}"
            asignacion_actual.finalizar(request.user)
            
            # Crear nueva asignación
            nueva_asignacion = AsignacionFarmacia(
                motorista=nuevo_motorista,
                farmacia=farmacia,
                creado_por=request.user,
                observaciones=f"Asignación por reemplazo. Motorista anterior: {asignacion_actual.motorista}"
            )
            nueva_asignacion.save()
            
            messages.success(request, 'Motorista reemplazado exitosamente.')
            return redirect('asignacion:listar_farmacias')
    else:
        form = ReemplazarMotoristaForm(farmacia_id)
    
    context = {
        'form': form,
        'farmacia': farmacia,
        'asignacion_actual': asignacion_actual,
        'titulo': 'Reemplazar Motorista'
    }
    
    return render(request, 'asignacion/reemplazar_motorista.html', context)

@login_required
@permission_required('asignacion.view_asignacionfarmacia', raise_exception=True)
def detalle_asignacion_farmacia(request, id):
    """Muestra el detalle de una asignación de farmacia"""
    asignacion = get_object_or_404(AsignacionFarmacia, id=id, activo=True)
    context = {
        'asignacion': asignacion,
        'titulo': 'Detalle Asignación de Farmacia'
    }
    return render(request, 'asignacion/detalle_farmacia.html', context)

# API endpoints para validaciones en tiempo real
@login_required
@permission_required('asignacion.view_asignacionmoto', raise_exception=True)
def validar_motorista_disponible(request):
    """Valida si un motorista está disponible para asignación"""
    from apps.motorista.models import Motorista
    
    motorista_rut = request.GET.get('motorista_rut')
    tipo = request.GET.get('tipo')  # 'moto' o 'farmacia'
    
    if motorista_rut and tipo:
        motorista = Motorista.objects.get(rut=motorista_rut, activo=True)
        
        if tipo == 'moto':
            # Verificar si ya tiene asignación activa de moto
            tiene_asignacion = AsignacionMoto.objects.filter(
                motorista=motorista,
                estado='ACTIVA',
                activo=True
            ).exists()
            return JsonResponse({'disponible': not tiene_asignacion})
        
        elif tipo == 'farmacia':
            # Verificar si ya tiene asignación activa de farmacia
            tiene_asignacion = AsignacionFarmacia.objects.filter(
                motorista=motorista,
                estado='ACTIVA',
                activo=True
            ).exists()
            # Verificar si tiene moto asignada
            tiene_moto = AsignacionMoto.objects.filter(
                motorista=motorista,
                estado='ACTIVA',
                activo=True
            ).exists()
            return JsonResponse({
                'disponible': not tiene_asignacion,
                'tiene_moto': tiene_moto
            })
    
    return JsonResponse({'error': 'Parámetros inválidos'}, status=400)

@login_required
@permission_required('asignacion.view_asignacionmoto', raise_exception=True)
def validar_moto_disponible(request):
    """Valida si una moto está disponible para asignación"""
    from apps.moto.models import Moto
    
    moto_patente = request.GET.get('moto_patente')
    
    try:
        moto = Moto.objects.get(patente=moto_patente, activo=True)
        
        # Verificar si ya tiene asignación activa
        tiene_asignacion = AsignacionMoto.objects.filter(
            moto=moto,
            estado='ACTIVA',
            activo=True
        ).exists()
        
        # Verificar documentos
        documentos_ok = moto.documentos_completos()
        
        return JsonResponse({
            'disponible': not tiene_asignacion,
            'documentos_ok': documentos_ok
        })
    
    except Moto.DoesNotExist:
        return JsonResponse({'error': 'Moto no encontrada'}, status=404)
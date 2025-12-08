from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from .models import OrdenDespacho, Movimiento, BitacoraMovimiento
from .forms import (
    OrdenDespachoForm, MovimientoDirectoForm, MovimientoRecetaForm,
    MovimientoTrasladoForm, MovimientoReenvioForm, CambiarEstadoMovimientoForm,
    ReenvioRapidoForm
)
from apps.asignacion.models import AsignacionFarmacia
from apps.usuario.models import Usuario # Importar el modelo Usuario
from apps.motorista.models import Motorista


@login_required
@permission_required('movimiento.view_movimiento', raise_exception=True)
def dashboard_movimientos(request):
    """
    Dashboard para la gestión de movimientos. Muestra estadísticas clave.
    """
    # Si es motorista, solo muestra sus movimientos
    if hasattr(request.user, 'es_motorista') and request.user.es_motorista:
        total_movimientos = Movimiento.objects.filter(rutMotorista__usuario=request.user).count()
        movimientos_por_estado_raw = Movimiento.objects.filter(
            rutMotorista__usuario=request.user
        ).values('estado').annotate(total=Count('estado')).order_by('-total')
        ultimos_movimientos = Movimiento.objects.filter(
            rutMotorista__usuario=request.user
        ).select_related('rutMotorista', 'idFarmaciaOrigen').order_by('-fechaCreacion')[:10]
    else:
        total_movimientos = Movimiento.objects.count()
        movimientos_por_estado_raw = Movimiento.objects.values('estado').annotate(total=Count('estado')).order_by('-total')
        ultimos_movimientos = Movimiento.objects.select_related(
            'rutMotorista', 'idFarmaciaOrigen'
        ).order_by('-fechaCreacion')[:10]
    
    # Formatear los nombres de los estados para la plantilla
    movimientos_por_estado = [
        {'estado': item['estado'], 'total': item['total'], 'nombre_display': item['estado'].replace('_', ' ').capitalize()}
        for item in movimientos_por_estado_raw
    ]

    context = {
        'titulo': 'Dashboard de Movimientos',
        'total_movimientos': total_movimientos,
        'movimientos_por_estado': movimientos_por_estado,
        'ultimos_movimientos': ultimos_movimientos,
    }
    return render(request, 'movimiento/dashboard.html', context)


@login_required
@permission_required('movimiento.view_ordendespacho', raise_exception=True)
def dashboard_ordenes(request):
    """
    Dashboard para la gestión de órdenes de despacho.
    """
    total_ordenes = OrdenDespacho.objects.filter(activo=True).count()
    
    # Obtener conteo de órdenes por estado
    ordenes_por_estado = OrdenDespacho.objects.filter(activo=True).values(
        'estado'
    ).annotate(total=Count('estado')).order_by('-total')
    
    # Órdenes recientes
    ultimas_ordenes = OrdenDespacho.objects.filter(activo=True).select_related().prefetch_related('movimientos').order_by('-fecha_creacion')[:10]

    context = {
        'titulo': 'Dashboard de Órdenes de Despacho',
        'total_ordenes': total_ordenes,
        'ordenes_por_estado': ordenes_por_estado,
        'ultimas_ordenes': ultimas_ordenes,
    }
    return render(request, 'movimiento/dashboard_ordenes.html', context)


class MovimientoListView(LoginRequiredMixin, ListView):
    """
    Vista para listar todos los movimientos con filtros y paginación.
    """
    model = Movimiento
    template_name = 'movimiento/movimiento_list.html'
    context_object_name = 'movimientos'
    paginate_by = 15

    def get_queryset(self):
        # Si es motorista, solo muestra sus movimientos
        if hasattr(self.request.user, 'es_motorista') and self.request.user.es_motorista:
            queryset = Movimiento.objects.filter(
                rutMotorista__usuario=self.request.user
            ).select_related('rutMotorista', 'idFarmaciaOrigen', 'orden_despacho').order_by('-fechaCreacion')
        else:
            queryset = Movimiento.objects.select_related(
                'rutMotorista', 'idFarmaciaOrigen', 'orden_despacho'
            ).order_by('-fechaCreacion')

        # Búsqueda general
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(idMovimiento__icontains=search_query) |
                Q(rutMotorista__nombre_completo__icontains=search_query) |
                Q(idFarmaciaOrigen__nombre__icontains=search_query) |
                Q(clienteNombre__icontains=search_query) |
                Q(orden_despacho__numero_orden__icontains=search_query)
            )

        # Filtro por tipo
        tipo = self.request.GET.get('tipo', '')
        if tipo:
            queryset = queryset.filter(tipoMovimiento=tipo)

        # Filtro por estado
        estado = self.request.GET.get('estado', '')
        if estado:
            queryset = queryset.filter(estado=estado)

        # Filtro por orden de despacho
        orden = self.request.GET.get('orden', '')
        if orden:
            queryset = queryset.filter(orden_despacho__numero_orden__icontains=orden)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Movimientos'
        context['search_query'] = self.request.GET.get('q', '')
        context['tipo_filtro'] = self.request.GET.get('tipo', '')
        context['estado_filtro'] = self.request.GET.get('estado', '')
        context['orden_filtro'] = self.request.GET.get('orden', '')
        context['tipos_movimiento'] = Movimiento.TIPO_MOVIMIENTO_CHOICES
        context['estados_movimiento'] = Movimiento.ESTADO_CHOICES
        # Añadir una instancia del formulario de cambio de estado para usar en los modales
        context['estado_form'] = CambiarEstadoMovimientoForm()
        return context


class OrdenDespachoListView(LoginRequiredMixin, ListView):
    """
    Vista para listar todas las órdenes de despacho.
    """
    model = OrdenDespacho
    template_name = 'movimiento/ordendespacho_list.html'
    context_object_name = 'ordenes'
    paginate_by = 15

    def get_queryset(self):
        queryset = OrdenDespacho.objects.filter(activo=True).prefetch_related(
            'movimientos'
        ).order_by('-fecha_creacion')

        # Búsqueda general
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(numero_orden__icontains=search_query) |
                Q(cliente_nombre__icontains=search_query) |
                Q(cliente_telefono__icontains=search_query) |
                Q(id_compra_online__icontains=search_query)
            )

        # Filtro por estado
        estado = self.request.GET.get('estado', '')
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Órdenes de Despacho'
        context['search_query'] = self.request.GET.get('q', '')
        context['estado_filtro'] = self.request.GET.get('estado', '')
        context['estados_orden'] = OrdenDespacho.ESTADO_CHOICES
        return context


class OrdenDespachoDetailView(LoginRequiredMixin, DetailView):
    """
    Vista para mostrar el detalle completo de una orden de despacho.
    """
    model = OrdenDespacho
    template_name = 'movimiento/ordendespacho_detail.html'
    context_object_name = 'orden'

    def get_queryset(self):
        return OrdenDespacho.objects.filter(activo=True).prefetch_related(
            'movimientos',
            'movimientos__rutMotorista',
            'movimientos__idFarmaciaOrigen',
            'movimientos__directo',
            'movimientos__receta',
            'movimientos__traslado',
            'movimientos__reenvio'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orden = self.get_object()
        
        # Realizar cálculos de movimientos en la vista
        movimientos_totales = orden.movimientos.count()
        movimientos_entregados = orden.movimientos.filter(estado='entregado').count()
        movimientos_pendientes = movimientos_totales - movimientos_entregados
        if movimientos_totales > 0:
            porcentaje_completado = (movimientos_entregados / movimientos_totales) * 100
        else:
            porcentaje_completado = 0
        
        context['titulo'] = f'Detalle Orden #{self.object.numero_orden}'
        context['movimientos_totales'] = movimientos_totales
        context['movimientos_entregados'] = movimientos_entregados
        context['movimientos_pendientes'] = movimientos_pendientes
        context['porcentaje_completado'] = porcentaje_completado
        return context


@login_required
@permission_required('movimiento.view_movimiento', raise_exception=True)
def movimiento_detalle(request, pk):
    """
    Muestra el detalle completo de un movimiento, incluyendo su tipo específico
    y la bitácora de cambios.
    """
    # Si es motorista, verifica que el movimiento le pertenezca
    if hasattr(request.user, 'es_motorista') and request.user.es_motorista:
        movimiento = get_object_or_404(
            Movimiento.objects.select_related(
                'rutMotorista', 'idFarmaciaOrigen', 'idFarmaciaDestino', 'autorizadoPor', 'orden_despacho',
                'directo', 'receta', 'traslado', 'reenvio', 'incidencias' # Añadir incidencias
            ).prefetch_related('bitacora__usuario'),
            pk=pk,
            rutMotorista=request.user.motorista
        )
    else:
        movimiento = get_object_or_404(
            Movimiento.objects.select_related(
                'rutMotorista', 'idFarmaciaOrigen', 'idFarmaciaDestino', 'autorizadoPor', 'orden_despacho',
                'directo', 'receta', 'traslado', 'reenvio', 'incidencias' # Añadir incidencias
            ).prefetch_related('bitacora__usuario'),
            pk=pk
        )

    # Formulario para cambiar estado
    estado_form = CambiarEstadoMovimientoForm(
        initial={'estado': movimiento.estado}, 
        current_state=movimiento.estado
    )

    context = {
        'titulo': f'Detalle Movimiento #{movimiento.idMovimiento}',
        'movimiento': movimiento,
        'estado_form': estado_form,
    }
    return render(request, 'movimiento/movimiento_detail.html', context)


@login_required
@permission_required('movimiento.change_movimiento', raise_exception=True)
def cambiar_estado_movimiento(request, pk):
    """Procesa el cambio de estado de un movimiento."""
    # Si es motorista, verifica que el movimiento le pertenezca
    if hasattr(request.user, 'es_motorista') and request.user.es_motorista:
        movimiento = get_object_or_404(
            Movimiento, 
            pk=pk,
            rutMotorista__usuario=request.user
        )
    else:
        movimiento = get_object_or_404(Movimiento, pk=pk)
        
    if request.method == 'POST':
        form = CambiarEstadoMovimientoForm(request.POST, current_state=movimiento.estado)
        if form.is_valid():
            estado_anterior = movimiento.get_estado_display()
            nuevo_estado = form.cleaned_data['estado']
            
            # Actualizar el movimiento
            movimiento.estado = nuevo_estado
            if nuevo_estado == 'entregado':
                movimiento.fechaEntrega = timezone.now()
            movimiento.save()

            # Registrar en la bitácora
            BitacoraMovimiento.objects.create(
                movimiento=movimiento,
                usuario=request.user,
                estadoAnterior=estado_anterior,
                estadoNuevo=movimiento.get_estado_display(),
                observaciones=form.cleaned_data['observaciones']
            )
            
            messages.success(
                request, 
                f"El estado del movimiento #{movimiento.idMovimiento} ha sido actualizado a '{movimiento.get_estado_display()}'."
            )
        else:
            messages.error(request, "Hubo un error al cambiar el estado. Por favor, inténtelo de nuevo.")
    
    return redirect('movimiento:detail', pk=movimiento.pk)


@login_required
@permission_required('movimiento.add_ordendespacho', raise_exception=True)
def crear_orden_despacho(request):
    """
    Vista para crear una nueva orden de despacho.
    """
    if request.method == 'POST':
        form = OrdenDespachoForm(request.POST)
        if form.is_valid():
            orden = form.save()
            messages.success(request, f'Orden #{orden.numero_orden} creada exitosamente.')
            return redirect('movimiento:orden_detalle', pk=orden.pk)
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = OrdenDespachoForm()

    context = {
        'form': form,
        'titulo': 'Crear Orden de Despacho'
    }
    return render(request, 'movimiento/ordendespacho_form.html', context)


@login_required
@permission_required('movimiento.add_movimiento', raise_exception=True)
def crear_movimiento_con_orden(request, tipo, orden_id):
    """
    Vista para crear movimientos con una orden específica pre-seleccionada.
    """
    form_map = {
        'directo': (MovimientoDirectoForm, 'Crear Movimiento Directo'),
        'receta': (MovimientoRecetaForm, 'Crear Movimiento con Receta'),
        'traslado': (MovimientoTrasladoForm, 'Crear Movimiento de Traslado'),
        'reenvio': (MovimientoReenvioForm, 'Crear Movimiento de Reenvío'),
    }

    form_class, titulo = form_map.get(tipo, (None, None))

    if not form_class:
        messages.error(request, "Tipo de movimiento no válido.")
        return redirect('movimiento:dashboard')

    try:
        orden_despacho = OrdenDespacho.objects.get(pk=orden_id, activo=True)
    except OrdenDespacho.DoesNotExist:
        messages.warning(request, "La orden de despacho especificada no existe.")
        return redirect('movimiento:seleccionar_orden', tipo=tipo)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            movimiento = form.save(autor=request.user)
            
            messages.success(
                request, 
                f'{titulo.replace("Crear ", "")} creado exitosamente. '
                f'Movimiento #{movimiento.idMovimiento} vinculado a la orden #{movimiento.orden_despacho.numero_orden}.'
            )
                
            return redirect('movimiento:detail', pk=movimiento.pk)
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        # Pre-seleccionar la orden
        initial_data = {'orden_despacho': orden_despacho}
        form = form_class(initial=initial_data)

    context = {
        'form': form,
        'titulo': titulo,
        'tipo_movimiento': tipo.capitalize(),
        'orden_despacho': orden_despacho
    }
    return render(request, 'movimiento/movimiento_form.html', context)


@login_required
@permission_required('movimiento.add_movimiento', raise_exception=True)
def crear_movimiento(request, tipo):
    """
    Vista genérica para crear movimientos - MODIFICADA para redirigir a selección de orden
    """
    # Redirigir a selección de orden
    return redirect('movimiento:seleccionar_orden', tipo=tipo)


@login_required
@permission_required('movimiento.add_movimiento', raise_exception=True)
def seleccionar_orden_movimiento(request, tipo):
    """
    Vista para seleccionar una orden existente o crear una nueva
    """
    ordenes_activas = OrdenDespacho.objects.filter(
        activo=True, 
        estado__in=['pendiente', 'en_proceso']
    ).order_by('-fecha_creacion')[:10]  # Últimas 10 órdenes activas

    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'seleccionar_existente':
            orden_id = request.POST.get('orden_existente')
            if orden_id:
                return redirect('movimiento:crear_con_orden', tipo=tipo, orden_id=orden_id)
            else:
                messages.error(request, 'Debe seleccionar una orden existente.')
                
        elif accion == 'crear_nueva':
            return redirect('movimiento:crear_orden_para_movimiento', tipo=tipo)

    context = {
        'titulo': f'Seleccionar Orden - Movimiento {tipo.capitalize()}',
        'tipo_movimiento': tipo,
        'ordenes_activas': ordenes_activas,
    }
    return render(request, 'movimiento/seleccionar_orden.html', context)


@login_required
@permission_required('movimiento.add_ordendespacho', raise_exception=True)
def crear_orden_para_movimiento(request, tipo):
    """
    Crear orden específicamente para un movimiento
    """
    if request.method == 'POST':
        form = OrdenDespachoForm(request.POST)
        if form.is_valid():
            orden = form.save()
            messages.success(request, f'Orden #{orden.numero_orden} creada exitosamente.')
            
            # Redirigir a crear movimiento con esta orden
            return redirect('movimiento:crear_con_orden', tipo=tipo, orden_id=orden.pk)
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = OrdenDespachoForm()

    context = {
        'form': form,
        'titulo': f'Crear Orden para Movimiento {tipo.capitalize()}',
        'tipo_movimiento': tipo
    }
    return render(request, 'movimiento/ordendespacho_form.html', context)


@login_required
@permission_required('movimiento.change_movimiento', raise_exception=True)
def crear_reenvio_rapido(request, pk):
    """
    Vista para crear reenvíos rápidos desde el detalle de un movimiento.
    """
    movimiento_original = get_object_or_404(Movimiento, pk=pk)
    
    if request.method == 'POST':
        form = ReenvioRapidoForm(request.POST, movimiento_original=movimiento_original)
        if form.is_valid():
            try:
                nuevo_movimiento = movimiento_original.crear_reenvio(
                    motivo=form.cleaned_data['motivoReenvio'],
                    nueva_direccion=form.cleaned_data['nuevaDireccion'],
                    nueva_fecha=form.cleaned_data['nuevaFecha'],
                    usuario=request.user
                )
                messages.success(
                    request, 
                    f'Reenvío creado exitosamente. Nuevo movimiento: #{nuevo_movimiento.idMovimiento}'
                )
                return redirect('movimiento:detail', pk=nuevo_movimiento.pk)
            except Exception as e:
                messages.error(request, f'Error al crear el reenvío: {str(e)}')
    else:
        form = ReenvioRapidoForm(movimiento_original=movimiento_original)

    context = {
        'form': form,
        'titulo': f'Crear Reenvío - Movimiento #{movimiento_original.idMovimiento}',
        'movimiento_original': movimiento_original
    }
    return render(request, 'movimiento/reenvio_rapido_form.html', context)


@login_required
def api_motoristas_por_farmacia(request, farmacia_id):
    """
    API que devuelve los motoristas asignados a una farmacia específica
    """
    try:
        # Verificar que la farmacia existe y está activa
        from apps.farmacia.models import Farmacia
        farmacia = get_object_or_404(Farmacia, id=farmacia_id, activo=True)
        
        # Obtener asignaciones activas para la farmacia
        asignaciones_activas = AsignacionFarmacia.objects.filter(
            farmacia_id=farmacia_id,
            estado='ACTIVA',
            activo=True
        ).select_related('motorista')
        
        motoristas_data = []
        for asignacion in asignaciones_activas:
            motorista = asignacion.motorista
            if motorista.activo:
                motoristas_data.append({
                    'id': motorista.id,
                    'nombre_completo': motorista.nombre_completo,
                    'rut': motorista.rut,
                    'telefono': motorista.telefono or 'No disponible'
                })
        
        return JsonResponse({
            'success': True,
            'farmacia': farmacia.nombre,
            'motoristas': motoristas_data,
            'total': len(motoristas_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@permission_required('movimiento.view_ordendespacho', raise_exception=True)
def api_ordenes_activas(request):
    """
    API que devuelve las órdenes de despacho activas para selects
    """
    try:
        ordenes = OrdenDespacho.objects.filter(
            activo=True, 
            estado__in=['pendiente', 'en_proceso']
        ).values('idOrden', 'numero_orden', 'cliente_nombre', 'estado')
        
        ordenes_data = list(ordenes)
        
        return JsonResponse({
            'success': True,
            'ordenes': ordenes_data,
            'total': len(ordenes_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
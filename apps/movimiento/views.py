from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Movimiento, BitacoraMovimiento
from .forms import (
    MovimientoDirectoForm,
    MovimientoRecetaForm,
    MovimientoTrasladoForm,
    MovimientoReenvioForm,
    CambiarEstadoMovimientoForm,
)


@login_required
def dashboard_movimientos(request):
    """
    Dashboard para la gestión de movimientos. Muestra estadísticas clave.
    """
    total_movimientos = Movimiento.objects.count()
    
    # Obtener conteo de movimientos por estado
    movimientos_por_estado_raw = Movimiento.objects.values('estado').annotate(total=Count('estado')).order_by('-total')
    
    # Formatear los nombres de los estados para la plantilla
    movimientos_por_estado = [
        {'estado': item['estado'], 'total': item['total'], 'nombre_display': item['estado'].replace('_', ' ').capitalize()}
        for item in movimientos_por_estado_raw
    ]
    
    ultimos_movimientos = Movimiento.objects.select_related(
        'rutMotorista', 'idFarmaciaOrigen'
    ).order_by('-fechaCreacion')[:10]

    context = {
        'titulo': 'Dashboard de Movimientos',
        'total_movimientos': total_movimientos,
        'movimientos_por_estado': movimientos_por_estado,
        'ultimos_movimientos': ultimos_movimientos,
    }
    return render(request, 'movimiento/dashboard.html', context)


class MovimientoListView(LoginRequiredMixin, ListView):
    """
    Vista para listar todos los movimientos con filtros y paginación.
    """
    model = Movimiento
    template_name = 'movimiento/movimiento_list.html'
    context_object_name = 'movimientos'
    paginate_by = 15

    def get_queryset(self):
        queryset = Movimiento.objects.select_related(
            'rutMotorista', 'idFarmaciaOrigen'
        ).order_by('-fechaCreacion')

        # Búsqueda general
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(idMovimiento__icontains=search_query) |
                Q(rutMotorista__nombre_completo__icontains=search_query) |
                Q(idFarmaciaOrigen__nombre__icontains=search_query) |
                Q(clienteNombre__icontains=search_query)
            )

        # Filtro por tipo
        tipo = self.request.GET.get('tipo', '')
        if tipo:
            queryset = queryset.filter(tipoMovimiento=tipo)

        # Filtro por estado
        estado = self.request.GET.get('estado', '')
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Movimientos'
        context['search_query'] = self.request.GET.get('q', '')
        context['tipo_filtro'] = self.request.GET.get('tipo', '')
        context['estado_filtro'] = self.request.GET.get('estado', '')
        context['tipos_movimiento'] = Movimiento.TIPO_MOVIMIENTO_CHOICES
        context['estados_movimiento'] = Movimiento.ESTADO_CHOICES
        # Añadir una instancia del formulario de cambio de estado para usar en los modales
        context['estado_form'] = CambiarEstadoMovimientoForm()
        return context


@login_required
def movimiento_detalle(request, pk):
    """
    Muestra el detalle completo de un movimiento, incluyendo su tipo específico
    y la bitácora de cambios.
    """
    movimiento = get_object_or_404(Movimiento.objects.select_related(
            'rutMotorista', 'idFarmaciaOrigen', 'idFarmaciaDestino', 'autorizadoPor',
            'directo', 'receta', 'traslado', 'reenvio'
        ).prefetch_related('bitacora__usuario'),
        pk=pk
    )

    # Formulario para cambiar estado
    estado_form = CambiarEstadoMovimientoForm(initial={'estado': movimiento.estado}, current_state=movimiento.estado)

    context = {
        'titulo': f'Detalle Movimiento #{movimiento.idMovimiento}',
        'movimiento': movimiento,
        'estado_form': estado_form,
    }
    return render(request, 'movimiento/movimiento_detail.html', context)


# --- Vistas de Creación de Movimientos ---

@login_required
def cambiar_estado_movimiento(request, pk):
    """Procesa el cambio de estado de un movimiento."""
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
            
            messages.success(request, f"El estado del movimiento #{movimiento.idMovimiento} ha sido actualizado a '{movimiento.get_estado_display()}'.")
        else:
            messages.error(request, "Hubo un error al cambiar el estado. Por favor, inténtelo de nuevo.")
    
    return redirect('movimiento:detail', pk=movimiento.pk)


@login_required
def crear_movimiento(request, tipo):
    """
    Vista genérica para crear movimientos.
    El 'tipo' se pasa por la URL ('directo', 'receta', 'traslado', 'reenvio').
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

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            # Pasamos el usuario para que el formulario lo asigne
            form.save(autor=request.user)
            messages.success(request, f'{titulo.replace("Crear ", "")} creado exitosamente.')
            return redirect('movimiento:list')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = form_class()

    context = {
        'form': form,
        'titulo': titulo,
        'tipo_movimiento': tipo.capitalize()
    }
    return render(request, 'movimiento/movimiento_form.html', context)

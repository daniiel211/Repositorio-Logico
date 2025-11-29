# apps/motorista/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Motorista
from .forms import MotoristaForm

# Mixins personalizados para permisos
class PermisoRequeridoMixin(LoginRequiredMixin):
    """Mixin base para permisos"""
    raise_exception = True
    login_url = '/usuario/login/'

class SoloGerenteMixin(PermisoRequeridoMixin):
    """Solo accesible para gerentes"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perms(['motorista.add_motorista', 'motorista.change_motorista', 'motorista.delete_motorista']):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class GerenteSupervisorMixin(PermisoRequeridoMixin):
    """Accesible para gerentes y supervisores"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perms(['motorista.add_motorista', 'motorista.change_motorista']):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class SoloLecturaMixin(PermisoRequeridoMixin):
    """Solo permisos de visualización"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('motorista.view_motorista'):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class MotoristaListView(SoloLecturaMixin, ListView):
    """Lista de motoristas - Accesible para todos los roles con permiso de visualización"""
    model = Motorista
    template_name = 'motorista/motorista_list.html'
    context_object_name = 'motoristas'
    paginate_by = 10

    def get_queryset(self):
        queryset = Motorista.objects.all().order_by('-fecha_creacion')

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nombre__icontains=search_query) |
                Q(apellidoPaterno__icontains=search_query) |
                Q(apellidoMaterno__icontains=search_query) |
                Q(rut__icontains=search_query)
            )

        estado = self.request.GET.get('estado', '')
        if estado == 'activos':
            queryset = queryset.filter(activo=True)
        elif estado == 'inactivos':
            queryset = queryset.filter(activo=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['estado_filtro'] = self.request.GET.get('estado', '')
        # Agregar información de permisos para el template
        context['puede_crear'] = self.request.user.has_perm('motorista.add_motorista')
        context['puede_editar'] = self.request.user.has_perm('motorista.change_motorista')
        context['puede_eliminar'] = self.request.user.has_perm('motorista.delete_motorista')
        return context

class MotoristaCreateView(SoloGerenteMixin, CreateView):
    """Crear motorista - Solo gerentes"""
    model = Motorista
    form_class = MotoristaForm
    template_name = 'motorista/motorista_form.html'
    success_url = reverse_lazy('motorista:list')

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, 'Motorista creado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrija los errores en el formulario.')
        return super().form_invalid(form)

class MotoristaUpdateView(GerenteSupervisorMixin, UpdateView):
    """Editar motorista - Gerentes y supervisores"""
    model = Motorista
    form_class = MotoristaForm
    template_name = 'motorista/motorista_form.html'
    success_url = reverse_lazy('motorista:list')

    def form_valid(self, form):
        form.instance.modificado_por = self.request.user
        messages.success(self.request, 'Motorista actualizado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrija los errores en el formulario.')
        return super().form_invalid(form)

class MotoristaDeleteView(SoloGerenteMixin, View):
    """Eliminar motorista - Solo gerentes"""
    def post(self, request, pk):
        motorista = get_object_or_404(Motorista, pk=pk)
        motorista.soft_delete()
        messages.success(request, 'Motorista desactivado exitosamente.')
        return redirect('motorista:list')

class MotoristaReactivateView(SoloGerenteMixin, View):
    """Reactivar motorista - Solo gerentes"""
    def post(self, request, pk):
        motorista = get_object_or_404(Motorista, pk=pk)
        motorista.reactivar()
        messages.success(request, 'Motorista reactivado exitosamente.')
        return redirect('motorista:list')

class MotoristaSearchView(SoloLecturaMixin, View):
    """Búsqueda de motoristas - Accesible para todos con permiso de visualización"""
    def get(self, request):
        query = request.GET.get('q', '')
        if query:
            motoristas = Motorista.objects.filter(
                Q(nombre__icontains=query) |
                Q(apellidoPaterno__icontains=query) |
                Q(rut__icontains=query)
            ).filter(activo=True)[:10]
            data = [{
                'id': motorista.rut,
                'text': f"{motorista.nombre_completo()} - {motorista.rut}"
            } for motorista in motoristas]
        else:
            data = []
        return JsonResponse({'results': data})

class MotoristaDashboardView(SoloLecturaMixin, View):
    """Dashboard de motoristas - Accesible para todos con permiso de visualización"""
    template_name = 'motorista/dashboard.html'
    
    def get(self, request):
        # Verificar permisos adicionales para acciones
        puede_crear = request.user.has_perm('motorista.add_motorista')
        
        # Estadísticas
        total_motoristas = Motorista.objects.count()
        motoristas_activos = Motorista.objects.filter(activo=True).count()
        motoristas_inactivos = Motorista.objects.filter(activo=False).count()
        
        # Próximos controles (próximos 30 días)
        from datetime import date, timedelta
        hoy = date.today()
        proximo_mes = hoy + timedelta(days=30)
        
        controles_proximos = Motorista.objects.filter(
            fechaControl__range=[hoy, proximo_mes],
            activo=True
        ).order_by('fechaControl')[:5]
        
        # Licencias próximas a vencer (próximos 30 días)
        licencias_proximas_vencer = Motorista.objects.filter(
            fechaVencimiento__range=[hoy, proximo_mes],
            activo=True
        ).order_by('fechaVencimiento')[:5]
        
        # Últimos motoristas registrados
        ultimos_registros = Motorista.objects.all().order_by('-fecha_creacion')[:5]
        
        context = {
            'total_motoristas': total_motoristas,
            'motoristas_activos': motoristas_activos,
            'motoristas_inactivos': motoristas_inactivos,
            'controles_proximos': controles_proximos,
            'licencias_proximas_vencer': licencias_proximas_vencer,
            'ultimos_registros': ultimos_registros,
            'puede_crear': puede_crear,
        }
        
        return render(request, self.template_name, context)
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

# Mixins personalizados según el prompt
from .models import Farmacia
from .forms import FarmaciaForm

class PermisoRequeridoMixin(PermissionRequiredMixin):
    """Mixin base para permisos - Compatible con Django 5"""
    raise_exception = True
    login_url = '/usuario/acceso-denegado/'

class SoloGerenteMixin(PermisoRequeridoMixin):
    """Solo accesible para gerentes"""
    permission_required = [
        'farmacia.add_farmacia',
        'farmacia.change_farmacia', 
        'farmacia.delete_farmacia'
    ]

class GerenteSupervisorMixin(PermisoRequeridoMixin):
    """Accesible para gerentes y supervisores"""
    permission_required = [
        'farmacia.add_farmacia',
        'farmacia.change_farmacia'
    ]

class SoloLecturaMixin(PermisoRequeridoMixin):
    """Solo permisos de visualización"""
    permission_required = ['farmacia.view_farmacia']

# Vistas protegidas con mixins de permisos
class FarmaciaListView(LoginRequiredMixin, SoloLecturaMixin, ListView):
    """
    Lista de farmacias - Accesible para todos los roles autenticados
    Requiere permiso: farmacia.view_farmacia
    """
    model = Farmacia
    template_name = 'farmacia/farmacia_list.html'
    context_object_name = 'farmacias'
    paginate_by = 10
    permission_required = ['farmacia.view_farmacia']

    def get_queryset(self):
        queryset = Farmacia.objects.all().order_by('-fecha_creacion')

        # Filtro de búsqueda
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nombre__icontains=search_query) |
                Q(direccion__icontains=search_query) |
                Q(comuna__icontains=search_query) |
                Q(IdFarmacia__icontains=search_query)
            )

        # Filtro por estado
        estado = self.request.GET.get('estado', '')
        if estado == 'activas':
            queryset = queryset.filter(activo=True)
        elif estado == 'inactivas':
            queryset = queryset.filter(activo=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['estado_filtro'] = self.request.GET.get('estado', '')
        return context

class FarmaciaCreateView(LoginRequiredMixin, SoloGerenteMixin, CreateView):
    """
    Crear farmacia - Solo gerentes
    Requiere permiso: farmacia.add_farmacia
    """
    model = Farmacia
    form_class = FarmaciaForm
    template_name = 'farmacia/farmacia_form.html'
    success_url = reverse_lazy('farmacia:list')
    permission_required = ['farmacia.add_farmacia']

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, 'Farmacia creada exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrija los errores en el formulario.')
        return super().form_invalid(form)

class FarmaciaUpdateView(LoginRequiredMixin, GerenteSupervisorMixin, UpdateView):
    """
    Editar farmacia - Gerentes y supervisores
    Requiere permiso: farmacia.change_farmacia
    """
    model = Farmacia
    form_class = FarmaciaForm
    template_name = 'farmacia/farmacia_form.html'
    success_url = reverse_lazy('farmacia:list')
    permission_required = ['farmacia.change_farmacia']

    def form_valid(self, form):
        form.instance.modificado_por = self.request.user
        messages.success(self.request, 'Farmacia actualizada exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrija los errores en el formulario.')
        return super().form_invalid(form)

class FarmaciaDeleteView(LoginRequiredMixin, SoloGerenteMixin, View):
    """
    Desactivar farmacia - Solo gerentes
    Requiere permiso: farmacia.delete_farmacia
    """
    permission_required = ['farmacia.delete_farmacia']

    def post(self, request, pk):
        farmacia = get_object_or_404(Farmacia, pk=pk)
        farmacia.soft_delete()
        messages.success(request, 'Farmacia desactivada exitosamente.')
        return redirect('farmacia:list')

class FarmaciaReactiveView(LoginRequiredMixin, SoloGerenteMixin, View):
    """
    Reactivar farmacia - Solo gerentes
    Requiere permiso: farmacia.delete_farmacia (para reactivar)
    """
    permission_required = ['farmacia.delete_farmacia']

    def post(self, request, pk):
        farmacia = get_object_or_404(Farmacia, pk=pk)
        farmacia.reactivar()
        messages.success(request, 'Farmacia reactivada exitosamente.')
        return redirect('farmacia:list')

class FarmaciaSearchView(LoginRequiredMixin, SoloLecturaMixin, View):
    """
    Búsqueda de farmacias - Todos los roles autenticados
    Requiere permiso: farmacia.view_farmacia
    """
    permission_required = ['farmacia.view_farmacia']

    def get(self, request):
        query = request.GET.get('q', '')
        if query:
            farmacias = Farmacia.objects.filter(
                Q(nombre__contains=query) |
                Q(IdFarmacia__contains=query)
            ).filter(activo=True)[:10]
            data = [{
                'id': farmacia.IdFarmacia,
                'text': f"{farmacia.nombre} - {farmacia.direccion}"
            } for farmacia in farmacias]
        else:
            data = []
        return JsonResponse({'results': data})

class DashboardView(LoginRequiredMixin, SoloLecturaMixin, View):
    """
    Dashboard de farmacias - Todos los roles autenticados
    Requiere permiso: farmacia.view_farmacia
    """
    permission_required = ['farmacia.view_farmacia']

    def get(self, request):
        farmacias_activas = Farmacia.objects.filter(activo=True).count()
        farmacias_inactivas = Farmacia.objects.filter(activo=False).count()
        total_farmacias = farmacias_activas + farmacias_inactivas
        
        context = {
            'farmacias_activas': farmacias_activas,
            'farmacias_inactivas': farmacias_inactivas,
            'total_farmacias': total_farmacias,
        }
        return render(request, 'farmacia/dashboard.html', context)
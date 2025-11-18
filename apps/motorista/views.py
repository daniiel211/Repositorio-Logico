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

class MotoristaListView(LoginRequiredMixin, ListView):
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
        return context

class MotoristaCreateView(LoginRequiredMixin, CreateView):
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

class MotoristaUpdateView(LoginRequiredMixin, UpdateView):
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

class MotoristaDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        motorista = get_object_or_404(Motorista, pk=pk)
        motorista.soft_delete()
        messages.success(request, 'Motorista desactivado exitosamente.')
        return redirect('motorista:list')

class MotoristaReactivateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        motorista = get_object_or_404(Motorista, pk=pk)
        motorista.reactivar()
        messages.success(request, 'Motorista reactivado exitosamente.')
        return redirect('motorista:list')

class MotoristaSearchView(LoginRequiredMixin, View):
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

class MotoristaDashboardView(LoginRequiredMixin, View):
    template_name = 'motorista/dashboard.html'
    
    def get(self, request):
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
        }
        
        return render(request, self.template_name, context)
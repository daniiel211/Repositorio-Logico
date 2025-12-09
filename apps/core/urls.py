# apps/core/urls.py - CORREGIDO
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),  # Página pública
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),  # Dashboard principal
    # O usa la versión simple:
    # path('dashboard/', views.dashboard_simple, name='dashboard'),
    
    path('acerca/', views.acerca, name='acerca'),
    path('configuracion-sistema/', views.ConfiguracionSistemaView.as_view(), name='configuracion_sistema'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
]
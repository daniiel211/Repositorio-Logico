from django.urls import path
from . import views
from .views import DashboardView, ConfiguracionSistemaView

app_name = 'core'

urlpatterns = [
    # Vistas públicas
    path('', views.home, name='home'),
    path('acerca/', views.acerca, name='acerca'),
    
    # Vistas protegidas con permisos
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('estadisticas/', views.estadisticas_avanzadas, name='estadisticas_avanzadas'),
    path('configuracion-sistema/', ConfiguracionSistemaView.as_view(), name='configuracion_sistema'),
]
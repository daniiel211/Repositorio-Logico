from django.urls import path
from . import views

app_name = 'asignacion'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_asignaciones, name='dashboard'),
    
    # Asignaciones de Moto
    path('motos/', views.listar_asignaciones_moto, name='listar_motos'),
    path('motos/crear/', views.crear_asignacion_moto, name='crear_moto'),
    path('motos/<int:id>/', views.detalle_asignacion_moto, name='detalle_moto'),
    path('motos/<int:id>/finalizar/', views.finalizar_asignacion_moto, name='finalizar_moto'),
    
    # Asignaciones de Farmacia
    path('farmacias/', views.listar_asignaciones_farmacia, name='listar_farmacias'),
    path('farmacias/crear/', views.crear_asignacion_farmacia, name='crear_farmacia'),
    path('farmacias/<int:id>/', views.detalle_asignacion_farmacia, name='detalle_farmacia'),
    path('farmacias/<int:id>/finalizar/', views.finalizar_asignacion_farmacia, name='finalizar_farmacia'),
    path('farmacias/<str:farmacia_id>/reemplazar/', views.reemplazar_motorista, name='reemplazar_motorista'),
    
    # API endpoints
    path('api/validar-motorista/', views.validar_motorista_disponible, name='validar_motorista'),
    path('api/validar-moto/', views.validar_moto_disponible, name='validar_moto'),
]
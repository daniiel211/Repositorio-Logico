from django.urls import path
from . import views

app_name = 'reporte'

urlpatterns = [
    path('', views.dashboard_reportes, name='dashboard'),
    path('farmacia/', views.reporte_farmacia, name='farmacia'),
    path('motorista/', views.reporte_motorista, name='motorista'),
    path('moto/', views.reporte_moto, name='moto'),
    path('asignacion/', views.reporte_asignacion, name='asignacion'),
    path('movimiento/', views.reporte_movimiento, name='movimiento'),
    path('historial/', views.historial_reportes, name='historial'),
    path('incidencias/', views.reporte_incidencias, name='incidencias')
]
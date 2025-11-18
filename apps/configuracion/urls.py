from django.urls import path
from . import views

app_name = 'configuracion'

urlpatterns = [
    path('', views.dashboard_configuracion, name='dashboard'),
    path('incidencias/', views.lista_incidencias, name='lista_incidencias'),
    path('incidencias/<int:incidencia_id>/', views.detalle_incidencia, name='detalle_incidencia'),
    path('incidencias/reportar/', views.reportar_incidencia, name='reportar_incidencia'),
    path('incidencias/reportar/<int:movimiento_id>/', views.reportar_incidencia, name='reportar_incidencia_movimiento'),
    path('incidencias/<int:incidencia_id>/resolver/', views.resolver_incidencia, name='resolver_incidencia'),
    path('rangos-accion/', views.gestion_rangos_accion, name='gestion_rangos'),
    path('api/verificar-rango/<str:farmacia_id>/<str:lat>/<str:lng>/', views.api_verificar_rango, name='api_verificar_rango'),
]
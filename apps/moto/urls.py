from django.urls import path
from . import views

app_name = 'moto'

urlpatterns = [
    path('', views.dashboard_moto, name='dashboard'),
    path('listar/', views.listar_motos, name='listar'),
    path('crear/', views.crear_moto, name='crear'),
    path('editar/<str:patente>/', views.editar_moto, name='editar'),
    path('eliminar/<str:patente>/', views.eliminar_moto, name='eliminar'),
    path('reactivar/<str:patente>/', views.reactivar_moto, name='reactivar'),
    path('detalle/<str:patente>/', views.detalle_moto, name='detalle'),
]
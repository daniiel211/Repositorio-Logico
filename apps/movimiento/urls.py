from django.urls import path
from . import views

app_name = 'movimiento'

urlpatterns = [
    # Dashboard y Listados
    path('dashboard/', views.dashboard_movimientos, name='dashboard'),
    path('', views.MovimientoListView.as_view(), name='list'),
    path('<int:pk>/', views.movimiento_detalle, name='detail'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado_movimiento, name='cambiar_estado'),
    path('<int:pk>/reenvio-rapido/', views.crear_reenvio_rapido, name='reenvio_rapido'),

    # Creación de Movimientos - URLs CORREGIDAS
    path('crear/<str:tipo>/', views.crear_movimiento, name='crear'),
    path('crear/<str:tipo>/seleccionar-orden/', views.seleccionar_orden_movimiento, name='seleccionar_orden'),
    path('crear/<str:tipo>/nueva-orden/', views.crear_orden_para_movimiento, name='crear_orden_para_movimiento'),
    path('crear/<str:tipo>/con-orden/<uuid:orden_id>/', views.crear_movimiento_con_orden, name='crear_con_orden'),
    
    # Órdenes de Despacho
    path('ordenes/dashboard/', views.dashboard_ordenes, name='orden_dashboard'),
    path('ordenes/', views.OrdenDespachoListView.as_view(), name='orden_list'),
    path('ordenes/crear/', views.crear_orden_despacho, name='orden_crear'),
    path('ordenes/<uuid:pk>/', views.OrdenDespachoDetailView.as_view(), name='orden_detalle'),
    
    # APIs
    path('api/motoristas-por-farmacia/<int:farmacia_id>/', views.api_motoristas_por_farmacia, name='api_motoristas_farmacia'),
    path('api/ordenes-activas/', views.api_ordenes_activas, name='api_ordenes_activas'),
]
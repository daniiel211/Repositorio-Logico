from django.urls import path
from . import views

app_name = 'movimiento'

urlpatterns = [
    # Dashboard y Listados
    path('dashboard/', views.dashboard_movimientos, name='dashboard'),
    path('', views.MovimientoListView.as_view(), name='list'),
    path('<int:pk>/', views.movimiento_detalle, name='detail'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado_movimiento, name='cambiar_estado'),

    # Creación de Movimientos
    path('crear/<str:tipo>/', views.crear_movimiento, name='crear'),
]
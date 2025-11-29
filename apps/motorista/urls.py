# apps/motorista/urls.py
from django.urls import path
from . import views

app_name = 'motorista'

urlpatterns = [
    path('', views.MotoristaDashboardView.as_view(), name='dashboard'),
    path('listado/', views.MotoristaListView.as_view(), name='list'),
    path('crear/', views.MotoristaCreateView.as_view(), name='create'),
    path('editar/<str:pk>/', views.MotoristaUpdateView.as_view(), name='update'),
    path('desactivar/<str:pk>/', views.MotoristaDeleteView.as_view(), name='delete'),
    path('reactivar/<str:pk>/', views.MotoristaReactivateView.as_view(), name='reactivate'),
    path('buscar/', views.MotoristaSearchView.as_view(), name='search'),
]
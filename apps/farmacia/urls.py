from django.urls import path
from . import views

app_name = 'farmacia'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('list/', views.FarmaciaListView.as_view(), name='list'),
    path('crear/', views.FarmaciaCreateView.as_view(), name='create'),
    path('editar/<str:pk>/', views.FarmaciaUpdateView.as_view(), name='update'),
    path('desactivar/<str:pk>/', views.FarmaciaDeleteView.as_view(), name='delete'),
    path('reactivar/<str:pk>/', views.FarmaciaReactiveView.as_view(), name='reactivate'),
    path('buscar/', views.FarmaciaSearchView.as_view(), name='search'),
]
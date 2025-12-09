# apps/usuario/urls.py - ACTUALIZADO CON NUEVAS RUTAS
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuario'

urlpatterns = [
    # 1. AUTENTICACIÓN
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='usuario:login'), name='logout'),
    
    # 2. DASHBOARD ESPECÍFICO DE USUARIOS (nueva ruta)
    # Esta es la vista a la que se accede desde el sidebar > "Gestión de Usuarios"
    path('dashboard-usuario/', views.dashboard_usuario, name='dashboard_usuario'),
    
    # 3. AUTOGESTIÓN (accesible para todos)
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
    
    # 4. GESTIÓN DE USUARIOS (CRUD - controlado por permisos)
    # Nota: Se mantiene 'usuarios/' como prefijo para consistencia
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/desactivar/<int:usuario_id>/', views.desactivar_usuario, name='desactivar_usuario'),
    path('usuarios/activar/<int:usuario_id>/', views.activar_usuario, name='activar_usuario'),
    path('usuarios/detalle/<int:usuario_id>/', views.detalle_usuario, name='detalle_usuario'),
    
    # 5. DEPRECATED: La ruta 'dashboard/' original ahora redirige al dashboard principal
    # Se mantiene por compatibilidad, pero es mejor usar 'core:dashboard'
    path('dashboard/', views.dashboard, name='dashboard'),
]
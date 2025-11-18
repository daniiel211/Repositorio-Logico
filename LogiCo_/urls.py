from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Core
    path('', include('core.urls')),
    
    # Usuario y autenticación
    path('usuario/', include('apps.usuario.urls')),
    
    # Módulos de gestión
    path('farmacia/', include('apps.farmacia.urls')),
    path('motorista/', include('apps.motorista.urls')),
    path('moto/', include('apps.moto.urls')),
    path('asignacion/', include('apps.asignacion.urls')),
    path('movimiento/', include('apps.movimiento.urls')),
    path('reporte/', include('apps.reporte.urls')),
    path('configuracion/', include('apps.configuracion.urls')),
]


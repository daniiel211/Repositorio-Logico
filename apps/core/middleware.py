# apps/core/middleware.py - ARCHIVO SIMPLIFICADO
import time
import logging
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.contrib import messages

logger = logging.getLogger(__name__)

class AuditoriaMiddleware:
    """
    Middleware para auditoría de accesos
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Método principal que maneja cada request"""
        
        # Procesamiento antes de la vista
        request.start_time = time.time()
        
        # Llamar a la vista
        response = self.get_response(request)

        # Procesamiento después de la vista
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Auditoría de acceso
            if request.user.is_authenticated and duration > 1.0:
                logger.info(f"Request lento: {request.path} - {duration:.2f}s - Usuario: {request.user} - Rol: {getattr(request.user, 'rol', 'sin rol')}")
                
        return response

class ValidacionPermisosMiddleware:
    """
    Middleware personalizado para validaciones básicas de permisos
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Método principal que maneja cada request"""
        
        # Solo validar para usuarios autenticados
        if request.user.is_authenticated:
            # Bloquear motoristas de secciones administrativas específicas
            if hasattr(request.user, 'es_motorista') and request.user.es_motorista:
                if any(path in request.path for path in ['/admin/', '/configuracion-sistema/']):
                    messages.error(request, 'Acceso restringido para motoristas.')
                    return redirect(reverse('core:dashboard'))
        
        return self.get_response(request)

class SeguridadHeadersMiddleware:
    """
    Middleware para agregar headers de seguridad
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Agregar headers de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # CSP básico
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:;"
        )
        
        return response
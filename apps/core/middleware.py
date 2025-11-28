import time
import logging
from django.shortcuts import redirect
from django.urls import resolve
from django.contrib import messages

logger = logging.getLogger(__name__)

class AuditoriaMiddleware:
    """
    Middleware para auditoría de accesos y validación de permisos
    Compatible con Django 5
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs que no requieren autenticación
        self.urls_publicas = [
            'core:home',
            'core:acerca',
            'usuario:login',
            'usuario:logout',
        ]

    def __call__(self, request):
        """Método principal que maneja cada request"""
        
        # Procesamiento antes de la vista
        request.start_time = time.time()
        
        # Validación adicional de permisos para URLs sensibles
        if request.user.is_authenticated:
            self._validar_acceso_urls_sensibles(request)

        # Llamar a la vista
        response = self.get_response(request)

        # Procesamiento después de la vista
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Auditoría de acceso
            if request.user.is_authenticated:
                self._registrar_auditoria(request, response, duration)
                
        return response

    def _validar_acceso_urls_sensibles(self, request):
        """
        Validación adicional para URLs sensibles
        Previene acceso a funcionalidades administrativas por roles no autorizados
        """
        try:
            resolver_match = resolve(request.path_info)
            url_name = resolver_match.url_name
            app_name = resolver_match.app_name

            # Validar acceso a configuraciones del sistema
            if url_name == 'configuracion_sistema' and app_name == 'core':
                if not request.user.has_perm('core.change_configuracionsistema'):
                    messages.error(request, 'No tiene permisos para acceder a la configuración del sistema')
                    # Redirigir al dashboard en lugar de mostrar 403 inmediatamente
                    from django.urls import reverse
                    return redirect(reverse('core:dashboard'))
                    
        except Exception as e:
            logger.warning(f"Error en validación de acceso: {e}")

    def _registrar_auditoria(self, request, response, duration):
        """
        Registra información de auditoría
        (Implementar cuando se tenga el modelo de auditoría)
        """
        # Ejemplo de implementación futura:
        # from .models import AuditoriaAcceso
        # AuditoriaAcceso.objects.create(
        #     usuario=request.user,
        #     url=request.path,
        #     metodo=request.method,
        #     estado_respuesta=response.status_code,
        #     duracion=duration,
        #     user_agent=request.META.get('HTTP_USER_AGENT', '')
        # )
        
        # Log temporal para debugging
        if duration > 1.0:  # Log solo requests lentos
            logger.info(f"Request lento: {request.path} - {duration:.2f}s - Usuario: {request.user}")

class ValidacionPermisosMiddleware:
    """
    Middleware personalizado para validaciones adicionales de permisos
    Compatible con Django 5
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Método principal que maneja cada request"""
        
        # Validaciones previas a la ejecución de la vista
        response = self._validar_acceso_motorista(request)
        if response:
            return response
            
        # Si no hay problemas, continuar con la vista normal
        response = self.get_response(request)
        return response

    def _validar_acceso_motorista(self, request):
        """
        Valida que usuarios motorista no accedan a funcionalidades administrativas
        """
        if request.user.is_authenticated and hasattr(request.user, 'es_motorista'):
            if request.user.es_motorista:
                # Bloquear acceso a URLs administrativas
                urls_bloqueadas = [
                    '/admin/',
                    '/usuario/lista',
                    '/configuracion/',
                    '/reportes/',
                ]
                
                if any(request.path.startswith(url) for url in urls_bloqueadas):
                    from django.http import HttpResponseForbidden
                    return HttpResponseForbidden(
                        "<h1>Acceso Denegado</h1>"
                        "<p>No tiene permisos para acceder a esta sección administrativa.</p>"
                        "<p>Su rol de motorista solo permite acceso a funcionalidades operativas.</p>"
                    )
        
        return None

class SeguridadHeadersMiddleware:
    """
    Middleware para agregar headers de seguridad
    Compatible con Django 5
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Agregar headers de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # CSP básico (ajustar según necesidades)
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:;"
        )
        
        return response
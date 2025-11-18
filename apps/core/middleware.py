import time
from django.utils.deprecation import MiddlewareMixin

class AuditoriaMiddleware(MiddlewareMixin):
    """Middleware básico para auditoría de accesos"""
    
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            # Aquí puedes guardar la auditoría en la base de datos
            if request.user.is_authenticated:
                pass
                # Log de acceso (implementar cuando tengas el modelo de auditoría)
        return response
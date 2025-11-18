from django.http import HttpResponseForbidden
from functools import wraps

def require_roles(allowed_roles):
    """
    Decorator para restringir acceso a vistas basado en roles de usuario.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Acceso denegado")
            
            user_role = getattr(request.user, 'rol', None)
            
            # Gerente tiene acceso completo
            if user_role == 'gerente':
                return view_func(request, *args, **kwargs)
            
            # Verificar si el rol del usuario está en los permitidos
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            return HttpResponseForbidden("No tiene permisos para acceder a esta sección")
        
        return _wrapped_view
    return decorator
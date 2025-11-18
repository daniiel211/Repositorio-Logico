from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps

def require_roles(allowed_roles):
    """
    Decorador personalizado para control de acceso basado en roles.
    
    Args:
        allowed_roles (list): Lista de roles permitidos para acceder a la vista
    
    Returns:
        function: Decorador que verifica permisos del usuario
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Verificar autenticación
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)

            # Verificar permisos: rol permitido o superusuario
            if request.user.rol in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("No tienes permisos para acceder a esta página")
        return _wrapped_view
    return decorator

def es_gerente(user):
    """Verifica si el usuario es gerente o superusuario"""
    return user.is_authenticated and (user.rol == 'gerente' or user.is_superuser)

def es_supervisor(user):
    """Verifica si el usuario es supervisor, gerente o superusuario"""
    return user.is_authenticated and (user.rol in ['gerente', 'supervisor'] or user.is_superuser)

def es_operador(user):
    """Verifica si el usuario es operador, supervisor, gerente o superusuario"""
    return user.is_authenticated and (user.rol in ['gerente', 'supervisor', 'operador'] or user.is_superuser)

def es_motorista(user):
    """Verifica si el usuario es motorista o superusuario"""
    return user.is_authenticated and (user.rol == 'motorista' or user.is_superuser)
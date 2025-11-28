from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.core.exceptions import PermissionDenied

def require_roles(allowed_roles):
    """
    Decorador personalizado para control de acceso basado en roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)

            if request.user.rol in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            raise PermissionDenied("No tienes permisos para acceder a esta página")
        return _wrapped_view
    return decorator

def require_permission(permission):
    """
    Decorador para verificar permisos específicos.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)
                
            if request.user.has_perm(permission) or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            raise PermissionDenied("No tienes permisos para realizar esta acción")
        return _wrapped_view
    return decorator

def can_edit_user():
    """
    Decorador para verificar si el usuario puede editar otro usuario.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)
                
            usuario_id = kwargs.get('usuario_id')
            from .models import Usuario
            
            # Superusuarios tienen acceso completo
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            # Usuario intentando editar su propio perfil
            if usuario_id and int(usuario_id) == request.user.id:
                return view_func(request, *args, **kwargs)
                
            # Verificar permisos según rol
            if request.user.es_gerente:
                return view_func(request, *args, **kwargs)
                
            if request.user.es_supervisor and request.user.has_perm('usuario.change_usuario'):
                return view_func(request, *args, **kwargs)
                
            raise PermissionDenied("No tienes permisos para editar este usuario")
        return _wrapped_view
    return decorator

def es_gerente(user):
    return user.is_authenticated and (user.rol == 'gerente' or user.is_superuser)

def es_supervisor(user):
    return user.is_authenticated and (user.rol in ['gerente', 'supervisor'] or user.is_superuser)

def es_operador(user):
    return user.is_authenticated and (user.rol in ['gerente', 'supervisor', 'operador'] or user.is_superuser)

def es_motorista(user):
    return user.is_authenticated and (user.rol == 'motorista' or user.is_superuser)
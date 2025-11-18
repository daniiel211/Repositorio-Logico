from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps

def require_roles(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)

            if request.user.rol in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("No tienes permisos para acceder a esta página")
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
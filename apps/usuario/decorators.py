# apps/usuario/decorators.py - CON MEJORES COMENTARIOS

from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.core.exceptions import PermissionDenied

def require_roles(allowed_roles):
    """
    Decorador personalizado para control de acceso basado en roles.
    
    USO: @require_roles(['gerente', 'supervisor'])
    
    FUNCIONALIDAD:
    1. Verifica que el usuario esté autenticado
    2. Comprueba si el rol del usuario está en allowed_roles
    3. Los superusuarios tienen acceso completo
    4. Si no cumple, lanza PermissionDenied
    
    EJEMPLOS:
    - Solo gerentes: @require_roles(['gerente'])
    - Gerentes y supervisores: @require_roles(['gerente', 'supervisor'])
    - Exclusivo motoristas: @require_roles(['motorista'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Verificar autenticación
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)

            # 2. Superusuarios tienen acceso completo
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # 3. Verificar si el rol está permitido
            if request.user.rol in allowed_roles:
                return view_func(request, *args, **kwargs)

            # 4. Acceso denegado
            raise PermissionDenied(f"Acceso denegado. Se requieren los roles: {', '.join(allowed_roles)}")
        return _wrapped_view
    return decorator

def require_permission(permission):
    """
    Decorador para verificar permisos específicos de Django.
    
    USO: @require_permission('usuario.view_usuario')
    
    FUNCIONALIDAD:
    1. Verifica que el usuario esté autenticado
    2. Comprueba si tiene el permiso específico
    3. Los superusuarios tienen acceso completo
    4. Ideal para control granular a nivel de modelo
    
    VENTAJAS:
    - Integración con sistema de permisos de Django
    - Puede usarse con grupos y permisos personalizados
    - Compatible con @permission_required de Django
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Verificar autenticación
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)
                
            # 2. Superusuarios tienen acceso completo
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            # 3. Verificar permiso específico
            if request.user.has_perm(permission):
                return view_func(request, *args, **kwargs)
                
            # 4. Acceso denegado
            raise PermissionDenied(f"No tienes permiso: {permission}")
        return _wrapped_view
    return decorator

def can_edit_user():
    """
    Decorador para verificar si el usuario puede editar otro usuario.
    
    USO: @can_edit_user()
    
    LÓGICA COMPLEJA:
    1. Superusuarios pueden editar cualquier usuario
    2. Usuarios pueden editar su propio perfil
    3. Gerentes pueden editar cualquier usuario
    4. Supervisores pueden editar usuarios (excepto gerentes, con permisos)
    5. Operadores solo pueden editar su propio perfil
    6. Motoristas solo pueden editar su propio perfil
    
    PARÁMETROS:
    - Espera un parámetro 'usuario_id' en kwargs
    - Compara con el ID del usuario actual
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Verificar autenticación
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)
                
            usuario_id = kwargs.get('usuario_id')
            from .models import Usuario
            
            # 2. Superusuarios tienen acceso completo
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            # 3. Usuario intentando editar su propio perfil (siempre permitido)
            if usuario_id and int(usuario_id) == request.user.id:
                return view_func(request, *args, **kwargs)
                
            # 4. Gerentes pueden editar cualquier usuario
            if request.user.es_gerente:
                return view_func(request, *args, **kwargs)
                
            # 5. Supervisores pueden editar si tienen permiso change_usuario
            if request.user.es_supervisor and request.user.has_perm('usuario.change_usuario'):
                return view_func(request, *args, **kwargs)
                
            # 6. Operadores y motoristas NO pueden editar otros usuarios
            raise PermissionDenied("No tienes permisos para editar este usuario")
        return _wrapped_view
    return decorator

# Funciones helper para uso en templates y lógica simple
def es_gerente(user):
    """Verifica si el usuario es gerente o superusuario"""
    return user.is_authenticated and (user.rol == 'gerente' or user.is_superuser)

def es_supervisor(user):
    """Verifica si el usuario es supervisor o superior"""
    return user.is_authenticated and (user.rol in ['gerente', 'supervisor'] or user.is_superuser)

def es_operador(user):
    """Verifica si el usuario es operador o superior"""
    return user.is_authenticated and (user.rol in ['gerente', 'supervisor', 'operador'] or user.is_superuser)

def es_motorista(user):
    """Verifica si el usuario es motorista"""
    return user.is_authenticated and (user.rol == 'motorista')
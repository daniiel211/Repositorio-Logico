from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView

from .decorators import require_roles, require_permission, can_edit_user
from .forms import LoginForm, UsuarioCreateForm, UsuarioUpdateForm, PasswordChangeCustomForm
from .models import Usuario

def login_view(request):
    """
    Vista personalizada para inicio de sesión.
    """
    if request.user.is_authenticated:
        return redirect('usuario:dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido/a {user.get_full_name()}')
                return redirect('usuario:dashboard')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')
    else:
        form = LoginForm()

    return render(request, 'usuario/login.html', {'form': form})

@login_required
def dashboard(request):
    """
    Dashboard principal con redirección por rol.
    """
    user = request.user
    
    # Importar modelos necesarios para evitar importaciones circulares
    from apps.farmacia.models import Farmacia
    from apps.motorista.models import Motorista
    from apps.moto.models import Moto
    from apps.movimiento.models import Movimiento
    from apps.asignacion.models import AsignacionMoto, AsignacionFarmacia
    from apps.configuracion.models import IncidenciaMovimiento
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Q, Count

    if user.es_gerente or user.is_superuser:
        # Lógica para dashboard gerente
        hoy = timezone.now().date()
        
        # Métricas básicas
        total_farmacias = Farmacia.objects.count()
        farmacias_activas = Farmacia.objects.filter(activo=True).count()
        total_motoristas = Motorista.objects.count()
        motoristas_activos = Motorista.objects.filter(activo=True).count()
        total_motos = Moto.objects.count()
        motos_activas = Moto.objects.filter(activo=True).count()
        
        # Usuarios activos
        usuarios_activos = Usuario.objects.filter(is_active=True).count()
        
        context = {
            'total_farmacias': total_farmacias,
            'farmacias_activas': farmacias_activas,
            'total_motoristas': total_motoristas,
            'motoristas_activos': motoristas_activos,
            'total_motos': total_motos,
            'motos_activas': motos_activas,
            'usuarios_activos': usuarios_activos,
        }
        return render(request, 'usuario/dashboard_gerente.html', context)
        
    elif user.es_supervisor:
        # Lógica para dashboard supervisor
        movimientos_pendientes = Movimiento.objects.filter(estado='pendiente').count()
        total_motoristas = Motorista.objects.filter(activo=True).count()
        
        context = {
            'movimientos_pendientes': movimientos_pendientes,
            'total_motoristas': total_motoristas,
        }
        return render(request, 'usuario/dashboard_supervisor.html', context)
        
    elif user.es_operador:
        # Lógica para dashboard operador
        hoy = timezone.now().date()
        movimientos_pendientes = Movimiento.objects.filter(estado='pendiente').count()
        movimientos_hoy = Movimiento.objects.filter(fechaCreacion__date=hoy).count()
        
        context = {
            'movimientos_pendientes': movimientos_pendientes,
            'movimientos_hoy': movimientos_hoy,
        }
        return render(request, 'usuario/dashboard_operador.html', context)
        
    elif user.es_motorista:
        # Lógica para dashboard motorista
        from apps.motorista.models import Motorista
        
        try:
            motorista = Motorista.objects.get(rut=user.rut)
        except Motorista.DoesNotExist:
            motorista = None
        
        if not motorista:
            context = {'error': 'No se encontró perfil de motorista asociado a su usuario.'}
            return render(request, 'usuario/dashboard_motorista.html', context)
        
        hoy = timezone.now().date()
        movimientos_asignados = Movimiento.objects.filter(
            rutMotorista=motorista, fechaCreacion__date=hoy
        ).count()
        
        movimientos_pendientes = Movimiento.objects.filter(
            rutMotorista=motorista, estado__in=['pendiente', 'en_camino']
        ).count()
        
        context = {
            'motorista': motorista,
            'movimientos_asignados': movimientos_asignados,
            'movimientos_pendientes': movimientos_pendientes,
        }
        return render(request, 'usuario/dashboard_motorista.html', context)
        
    else:
        return render(request, 'usuario/base_dashboard.html')

class UsuarioListView(PermissionRequiredMixin, ListView):
    """
    Vista basada en clase para listar usuarios con control de permisos.
    """
    model = Usuario
    template_name = 'usuario/lista_usuarios.html'
    context_object_name = 'usuarios'
    permission_required = 'usuario.view_usuario'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Usuario.objects.all()
        query = self.request.GET.get('q', '')
        rol_filter = self.request.GET.get('rol', '')
        estado_filter = self.request.GET.get('estado', '')

        # Aplicar filtros de búsqueda
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(rut__icontains=query)
            )

        if rol_filter:
            queryset = queryset.filter(rol=rol_filter)

        if estado_filter:
            if estado_filter == 'activo':
                queryset = queryset.filter(is_active=True)
            elif estado_filter == 'inactivo':
                queryset = queryset.filter(is_active=False)

        return queryset.order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['rol_filter'] = self.request.GET.get('rol', '')
        context['estado_filter'] = self.request.GET.get('estado', '')
        context['roles'] = Usuario.ROL_CHOICES
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # Motoristas no pueden ver la lista de usuarios
        if request.user.es_motorista:
            raise PermissionDenied("Los motoristas no pueden ver la lista de usuarios")
        return super().dispatch(request, *args, **kwargs)

@login_required
@require_permission('usuario.add_usuario')
def crear_usuario(request):
    """
    Crear nuevo usuario en el sistema.
    """
    # Operadores y motoristas no pueden crear usuarios
    if request.user.es_operador or request.user.es_motorista:
        raise PermissionDenied("No tienes permisos para crear usuarios")
    
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario {usuario.get_full_name()} creado exitosamente')
            return redirect('usuario:lista_usuarios')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')
    else:
        form = UsuarioCreateForm()

    return render(request, 'usuario/crear_usuario.html', {'form': form})

@login_required
@can_edit_user()
def editar_usuario(request, usuario_id):
    """
    Editar usuario existente con validaciones de permisos.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Validaciones adicionales de permisos
    if request.user.es_operador and usuario != request.user:
        raise PermissionDenied("Los operadores solo pueden editar su propio perfil")
    
    if request.user.es_motorista and usuario != request.user:
        raise PermissionDenied("Los motoristas solo pueden editar su propio perfil")

    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            # Validar que solo gerentes pueden cambiar roles a gerente
            if 'rol' in form.changed_data:
                nuevo_rol = form.cleaned_data.get('rol')
                if nuevo_rol == 'gerente' and not request.user.es_gerente and not request.user.is_superuser:
                    messages.error(request, 'Solo los gerentes pueden asignar el rol de gerente')
                    return render(request, 'usuario/editar_usuario.html', {'form': form, 'usuario': usuario})
            
            form.save()
            messages.success(request, f'Usuario {usuario.get_full_name()} actualizado exitosamente')
            
            # Redirigir según el tipo de usuario
            if request.user == usuario:
                return redirect('usuario:perfil')
            else:
                return redirect('usuario:lista_usuarios')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')
    else:
        form = UsuarioUpdateForm(instance=usuario)

    context = {
        'form': form,
        'usuario': usuario
    }
    return render(request, 'usuario/editar_usuario.html', context)

@login_required
@require_permission('usuario.change_usuario')
def desactivar_usuario(request, usuario_id):
    """
    Desactivar usuario (soft delete).
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Validaciones de seguridad
    if usuario == request.user:
        messages.error(request, 'No puedes desactivar tu propio usuario')
        return redirect('usuario:lista_usuarios')
    
    # Operadores y motoristas no pueden desactivar usuarios
    if request.user.es_operador or request.user.es_motorista:
        raise PermissionDenied("No tienes permisos para desactivar usuarios")
    
    if request.method == 'POST':
        usuario.is_active = False
        usuario.save()
        messages.success(request, f'Usuario {usuario.get_full_name()} desactivado exitosamente')
        return redirect('usuario:lista_usuarios')
    
    return render(request, 'usuario/confirmar_desactivar.html', {'usuario': usuario})

@login_required
@require_permission('usuario.change_usuario')
def activar_usuario(request, usuario_id):
    """
    Activar usuario previamente desactivado.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Operadores y motoristas no pueden activar usuarios
    if request.user.es_operador or request.user.es_motorista:
        raise PermissionDenied("No tienes permisos para activar usuarios")
    
    if request.method == 'POST':
        usuario.is_active = True
        usuario.save()
        messages.success(request, f'Usuario {usuario.get_full_name()} activado exitosamente')
        return redirect('usuario:lista_usuarios')
    
    return render(request, 'usuario/confirmar_activar.html', {'usuario': usuario})

@login_required
def perfil_usuario(request):
    """
    Perfil del usuario actual.
    Accesible para todos los usuarios autenticados.
    """
    usuario = request.user

    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            # Usuarios no gerentes no pueden cambiar su propio rol
            if 'rol' in form.changed_data and not request.user.es_gerente and not request.user.is_superuser:
                messages.error(request, 'No puedes cambiar tu propio rol')
                return render(request, 'usuario/perfil.html', {'form': form})
            
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente')
            return redirect('usuario:perfil')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')
    else:
        form = UsuarioUpdateForm(instance=usuario)

    return render(request, 'usuario/perfil.html', {'form': form})

@login_required
def cambiar_password(request):
    """
    Cambiar contraseña del usuario actual.
    Accesible para todos los usuarios autenticados.
    """
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña cambiada exitosamente')
            return redirect('usuario:perfil')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')
    else:
        form = PasswordChangeCustomForm(request.user)

    return render(request, 'usuario/cambiar_password.html', {'form': form})

@login_required
@require_permission('usuario.view_usuario')
def detalle_usuario(request, usuario_id):
    """
    Ver detalles de un usuario específico.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # Motoristas solo pueden ver su propio perfil
    if request.user.es_motorista and usuario != request.user:
        raise PermissionDenied("Los motoristas solo pueden ver su propio perfil")
    
    return render(request, 'usuario/detalle_usuario.html', {'usuario': usuario})

# Reemplazar la vista lista_usuarios por la vista basada en clase
lista_usuarios = UsuarioListView.as_view()
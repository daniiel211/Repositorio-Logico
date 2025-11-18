from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .decorators import require_roles
from .forms import LoginForm, UsuarioCreateForm, UsuarioUpdateForm, PasswordChangeCustomForm
from .models import Usuario

def login_view(request):
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
                messages.success(request, f'¡Bienvenido/a {user.get_full_name()}!')
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
    """Dashboard principal con redirección por rol"""
    user = request.user

    if user.es_gerente or user.is_superuser:
        return render(request, 'usuario/dashboard_gerente.html')
    elif user.es_supervisor:
        return render(request, 'usuario/dashboard_supervisor.html')
    elif user.es_operador:
        return render(request, 'usuario/dashboard_operador.html')
    elif user.es_motorista:
        return render(request, 'usuario/dashboard_motorista.html')
    else:
        return render(request, 'usuario/dashboard_base.html')

@login_required
@require_roles(['gerente'])
def lista_usuarios(request):
    """Lista todos los usuarios con opciones de búsqueda y filtro"""
    query = request.GET.get('q', '')
    rol_filter = request.GET.get('rol', '')
    estado_filter = request.GET.get('estado', '')

    usuarios = Usuario.objects.all()

    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(rut__icontains=query)
        )

    if rol_filter:
        usuarios = usuarios.filter(rol=rol_filter)

    if estado_filter:
        if estado_filter == 'activo':
            usuarios = usuarios.filter(is_active=True)
        elif estado_filter == 'inactivo':
            usuarios = usuarios.filter(is_active=False)

    usuarios = usuarios.order_by('-date_joined')

    context = {
        'usuarios': usuarios,
        'query': query,
        'rol_filter': rol_filter,
        'estado_filter': estado_filter,
        'roles': Usuario.ROL_CHOICES,
    }
    return render(request, 'usuario/lista_usuarios.html', context)

@login_required
@require_roles(['gerente'])
def crear_usuario(request):
    """Crear nuevo usuario"""
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
@require_roles(['gerente'])
def editar_usuario(request, usuario_id):
    """Editar usuario existente"""
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {usuario.get_full_name()} actualizado exitosamente')
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
@require_roles(['gerente'])
def desactivar_usuario(request, usuario_id):
    """Desactivar usuario"""
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if usuario == request.user:
        messages.error(request, 'No puedes desactivar tu propio usuario')
        return redirect('usuario:lista_usuarios')
    
    if request.method == 'POST':
        usuario.is_active = False
        usuario.save()
        messages.success(request, f'Usuario {usuario.get_full_name()} desactivado exitosamente')
        return redirect('usuario:lista_usuarios')
    
    return render(request, 'usuario/confirmar_desactivar.html', {'usuario': usuario})

@login_required
@require_roles(['gerente'])
def activar_usuario(request, usuario_id):
    """Activar usuario"""
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        usuario.is_active = True
        usuario.save()
        messages.success(request, f'Usuario {usuario.get_full_name()} activado exitosamente')
        return redirect('usuario:lista_usuarios')
    
    return render(request, 'usuario/confirmar_activar.html', {'usuario': usuario})

@login_required
def perfil_usuario(request):
    """Perfil del usuario actual"""
    usuario = request.user

    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
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
    """Cambiar contraseña del usuario actual"""
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
@require_roles(['gerente'])
def detalle_usuario(request, usuario_id):
    """Ver detalles de un usuario específico"""
    usuario = get_object_or_404(Usuario, id=usuario_id)
    return render(request, 'usuario/detalle_usuario.html', {'usuario': usuario})
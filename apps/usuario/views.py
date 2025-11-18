from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .decorators import require_roles
from .forms import LoginForm, UsuarioCreateForm, UsuarioUpdateForm, PasswordChangeCustomForm
from .models import Usuario

def login_view(request):
    """
    Vista personalizada para inicio de sesión.
    Redirige usuarios autenticados al dashboard.
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
    """
    Dashboard principal con redirección por rol.
    Renderiza templates específicos según el rol del usuario.
    """
    user = request.user
    
    # Importar modelos necesarios
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
        
        # Métricas de Farmacias
        total_farmacias = Farmacia.objects.count()
        farmacias_activas = Farmacia.objects.filter(activo=True).count()
        farmacias_inactivas = Farmacia.objects.filter(activo=False).count()
        
        # Métricas de Motoristas
        total_motoristas = Motorista.objects.count()
        motoristas_activos = Motorista.objects.filter(activo=True).count()
        motoristas_inactivos = Motorista.objects.filter(activo=False).count()
        
        # Métricas de Motos
        total_motos = Moto.objects.count()
        motos_activas = Moto.objects.filter(activo=True).count()
        
        # Métricas de Movimientos
        movimientos_hoy = Movimiento.objects.filter(fechaCreacion__date=hoy).count()
        movimientos_completados = Movimiento.objects.filter(
            fechaCreacion__date=hoy, estado='entregado'
        ).count()
        
        # Eficiencia general
        total_movimientos_periodo = Movimiento.objects.filter(
            fechaCreacion__date__gte=hoy - timedelta(days=7)
        ).count()
        movimientos_entregados_periodo = Movimiento.objects.filter(
            fechaCreacion__date__gte=hoy - timedelta(days=7), estado='entregado'
        ).count()
        
        eficiencia_general = 0
        if total_movimientos_periodo > 0:
            eficiencia_general = round((movimientos_entregados_periodo / total_movimientos_periodo) * 100, 1)
        
        # Usuarios activos
        from .models import Usuario
        usuarios_activos = Usuario.objects.filter(is_active=True).count()
        
        # Asignaciones activas
        asignaciones_activas = AsignacionMoto.objects.filter(
            estado='ACTIVA', activo=True
        ).count() + AsignacionFarmacia.objects.filter(
            estado='ACTIVA', activo=True
        ).count()
        
        # Incidencias pendientes
        incidencias_pendientes = IncidenciaMovimiento.objects.filter(
            estado__in=['REGISTRADA', 'EN_REVISION']
        ).count()
        
        # Movimientos recientes
        movimientos_recientes = Movimiento.objects.select_related(
            'rutMotorista', 'idFarmaciaOrigen'
        ).order_by('-fechaCreacion')[:10]

        context = {
            'total_farmacias': total_farmacias,
            'farmacias_activas': farmacias_activas,
            'farmacias_inactivas': farmacias_inactivas,
            'total_motoristas': total_motoristas,
            'motoristas_activos': motoristas_activos,
            'motoristas_inactivos': motoristas_inactivos,
            'total_motos': total_motos,
            'motos_activas': motos_activas,
            'movimientos_hoy': movimientos_hoy,
            'movimientos_completados': movimientos_completados,
            'eficiencia_general': eficiencia_general,
            'usuarios_activos': usuarios_activos,
            'asignaciones_activas': asignaciones_activas,
            'incidencias_pendientes': incidencias_pendientes,
            'movimientos_recientes': movimientos_recientes,
        }
        return render(request, 'usuario/dashboard_gerente.html', context)
        
    elif user.es_supervisor:
        # Lógica para dashboard supervisor
        movimientos_pendientes = Movimiento.objects.filter(estado='pendiente').count()
        
        asignaciones_activas = AsignacionMoto.objects.filter(
            estado='ACTIVA', activo=True
        ).count() + AsignacionFarmacia.objects.filter(
            estado='ACTIVA', activo=True
        ).count()
        
        motoristas_disponibles = Motorista.objects.filter(
            activo=True
        ).exclude(
            Q(asignacionmoto__estado='ACTIVA') | Q(asignacionfarmacia__estado='ACTIVA')
        ).count()
        
        total_motoristas = Motorista.objects.filter(activo=True).count()
        
        incidencias_activas = IncidenciaMovimiento.objects.filter(
            estado__in=['REGISTRADA', 'EN_REVISION']
        ).count()
        
        movimientos_atencion = Movimiento.objects.filter(
            estado__in=['pendiente', 'fallido', 'pendiente_autorizacion']
        ).select_related('rutMotorista', 'idFarmaciaOrigen')[:10]
        
        movimientos_atencion_count = movimientos_atencion.count()

        context = {
            'movimientos_pendientes': movimientos_pendientes,
            'asignaciones_activas': asignaciones_activas,
            'motoristas_disponibles': motoristas_disponibles,
            'total_motoristas': total_motoristas,
            'incidencias_activas': incidencias_activas,
            'movimientos_atencion': movimientos_atencion,
            'movimientos_atencion_count': movimientos_atencion_count,
        }
        return render(request, 'usuario/dashboard_supervisor.html', context)
        
    elif user.es_operador:
        # Lógica para dashboard operador
        hoy = timezone.now().date()
        
        movimientos_pendientes = Movimiento.objects.filter(estado='pendiente').count()
        movimientos_hoy = Movimiento.objects.filter(fechaCreacion__date=hoy).count()
        incidencias_activas = IncidenciaMovimiento.objects.filter(
            estado__in=['REGISTRADA', 'EN_REVISION']
        ).count()
        farmacias_activas = Farmacia.objects.filter(activo=True).count()
        motoristas_disponibles = Motorista.objects.filter(activo=True).count()
        
        movimientos_recientes = Movimiento.objects.filter(
            creado_por=user
        ).select_related('rutMotorista', 'idFarmaciaOrigen').order_by('-fechaCreacion')[:5]

        context = {
            'movimientos_pendientes': movimientos_pendientes,
            'movimientos_hoy': movimientos_hoy,
            'incidencias_activas': incidencias_activas,
            'farmacias_activas': farmacias_activas,
            'motoristas_disponibles': motoristas_disponibles,
            'movimientos_recientes': movimientos_recientes,
        }
        return render(request, 'usuario/dashboard_operador.html', context)
        
    elif user.es_motorista:
        # Lógica para dashboard motorista
        from apps.motorista.models import Motorista
        
        # Obtener el motorista asociado al usuario
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
        
        movimientos_completados = Movimiento.objects.filter(
            rutMotorista=motorista, estado='entregado', fechaCreacion__date=hoy
        ).count()
        
        total_movimientos = Movimiento.objects.filter(rutMotorista=motorista).count()
        movimientos_entregados = Movimiento.objects.filter(
            rutMotorista=motorista, estado='entregado'
        ).count()
        
        tasa_exito = 0
        if total_movimientos > 0:
            tasa_exito = round((movimientos_entregados / total_movimientos) * 100, 1)
        
        # Información de la moto asignada
        moto_asignada = None
        try:
            asignacion_moto = AsignacionMoto.objects.get(
                motorista=motorista, estado='ACTIVA', activo=True
            )
            moto_asignada = asignacion_moto.moto
        except AsignacionMoto.DoesNotExist:
            moto_asignada = None
        
        # Farmacias asignadas
        farmacias_asignadas = AsignacionFarmacia.objects.filter(
            motorista=motorista, estado='ACTIVA', activo=True
        ).select_related('farmacia')
        
        # Movimientos recientes
        movimientos_recientes = Movimiento.objects.filter(
            rutMotorista=motorista
        ).select_related('idFarmaciaOrigen').order_by('-fechaCreacion')[:5]

        context = {
            'motorista': motorista,
            'movimientos_asignados': movimientos_asignados,
            'movimientos_pendientes': movimientos_pendientes,
            'movimientos_completados': movimientos_completados,
            'total_movimientos': total_movimientos,
            'movimientos_entregados': movimientos_entregados,
            'tasa_exito': tasa_exito,
            'moto_asignada': moto_asignada,
            'farmacias_asignadas': farmacias_asignadas,
            'movimientos_recientes': movimientos_recientes,
        }
        return render(request, 'usuario/dashboard_motorista.html', context)
        
    else:
        return render(request, 'usuario/base_dashboard.html')

@login_required
@require_roles(['gerente'])
def lista_usuarios(request):
    """
    Lista todos los usuarios con opciones de búsqueda y filtro.
    Accesible solo para gerentes y superusuarios.
    """
    query = request.GET.get('q', '')
    rol_filter = request.GET.get('rol', '')
    estado_filter = request.GET.get('estado', '')

    usuarios = Usuario.objects.all()

    # Aplicar filtros de búsqueda
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
    """
    Crear nuevo usuario en el sistema.
    Accesible solo para gerentes y superusuarios.
    """
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
    """
    Editar usuario existente.
    Accesible solo para gerentes y superusuarios.
    """
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
    """
    Desactivar usuario (soft delete).
    Impide que un gerente se desactive a sí mismo.
    """
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
    """
    Activar usuario previamente desactivado.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
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
@require_roles(['gerente'])
def detalle_usuario(request, usuario_id):
    """
    Ver detalles de un usuario específico.
    Accesible solo para gerentes y superusuarios.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    return render(request, 'usuario/detalle_usuario.html', {'usuario': usuario})
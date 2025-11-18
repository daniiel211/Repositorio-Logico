"""
Script para crear usuarios, grupos y asignar permisos en el sistema LogiCo
Ejecutar: python manage.py shell < crear_usuarios_roles.py
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LogiCo_.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

User = get_user_model()

def crear_grupos_y_permisos():
    """Crea los grupos y asigna permisos según los roles del sistema"""
    
    print("CREANDO GRUPOS Y PERMISOS")
    
    # 1. GRUPO GERENTE (Acceso total)
    gerente_group, created = Group.objects.get_or_create(name='Gerentes')
    if created:
        print("Grupo 'Gerentes' creado")
    
    permisos_gerente = [
        # Usuario (acceso completo)
        'usuario.add_usuario', 'usuario.change_usuario', 'usuario.delete_usuario', 'usuario.view_usuario',
        # Farmacia (acceso completo)
        'farmacia.add_farmacia', 'farmacia.change_farmacia', 'farmacia.delete_farmacia', 'farmacia.view_farmacia',
        # Motorista (acceso completo)
        'motorista.add_motorista', 'motorista.change_motorista', 'motorista.delete_motorista', 'motorista.view_motorista',
        # Moto (acceso completo)
        'moto.add_moto', 'moto.change_moto', 'moto.delete_moto', 'moto.view_moto',
        # Asignación (acceso completo)
        'asignacion.add_asignacionfarmacia', 'asignacion.change_asignacionfarmacia', 'asignacion.delete_asignacionfarmacia', 'asignacion.view_asignacionfarmacia',
        'asignacion.add_asignacionmoto', 'asignacion.change_asignacionmoto', 'asignacion.delete_asignacionmoto', 'asignacion.view_asignacionmoto',
        'asignacion.can_manage_asignaciones',
        # Movimiento (acceso completo)
        'movimiento.add_movimiento', 'movimiento.change_movimiento', 'movimiento.delete_movimiento', 'movimiento.view_movimiento',
        'movimiento.add_movimientodirecto', 'movimiento.change_movimientodirecto', 'movimiento.delete_movimientodirecto', 'movimiento.view_movimientodirecto',
        'movimiento.add_movimientoreceta', 'movimiento.change_movimientoreceta', 'movimiento.delete_movimientoreceta', 'movimiento.view_movimientoreceta',
        'movimiento.add_movimientotraslado', 'movimiento.change_movimientotraslado', 'movimiento.delete_movimientotraslado', 'movimiento.view_movimientotraslado',
        'movimiento.add_movimientoreenvio', 'movimiento.change_movimientoreenvio', 'movimiento.delete_movimientoreenvio', 'movimiento.view_movimientoreenvio',
        'movimiento.add_bitacoramovimiento', 'movimiento.change_bitacoramovimiento', 'movimiento.delete_bitacoramovimiento', 'movimiento.view_bitacoramovimiento',
        'movimiento.add_estadomovimiento', 'movimiento.change_estadomovimiento', 'movimiento.delete_estadomovimiento', 'movimiento.view_estadomovimiento',
        # Reportes (acceso completo)
        'reporte.add_configuracionreporte', 'reporte.change_configuracionreporte', 'reporte.delete_configuracionreporte', 'reporte.view_configuracionreporte',
        'reporte.add_filtroreporte', 'reporte.change_filtroreporte', 'reporte.delete_filtroreporte', 'reporte.view_filtroreporte',
        'reporte.add_reportegenerado', 'reporte.change_reportegenerado', 'reporte.delete_reportegenerado', 'reporte.view_reportegenerado',
        # Configuración (acceso completo)
        'configuracion.add_configuracionsistema', 'configuracion.change_configuracionsistema', 'configuracion.delete_configuracionsistema', 'configuracion.view_configuracionsistema',
        'configuracion.add_rangoaccion', 'configuracion.change_rangoaccion', 'configuracion.delete_rangoaccion', 'configuracion.view_rangoaccion',
        'configuracion.add_tipoincidencia', 'configuracion.change_tipoincidencia', 'configuracion.delete_tipoincidencia', 'configuracion.view_tipoincidencia',
        'configuracion.add_incidenciamovimiento', 'configuracion.change_incidenciamovimiento', 'configuracion.delete_incidenciamovimiento', 'configuracion.view_incidenciamovimiento',
    ]
    
    for perm_codename in permisos_gerente:
        try:
            app_label, codename = perm_codename.split('.')
            perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
            gerente_group.permissions.add(perm)
        except Permission.DoesNotExist:
            print(f"Permiso no encontrado: {perm_codename}")
    
    print(f"Permisos asignados a Gerentes: {gerente_group.permissions.count()}")

    # 2. GRUPO SUPERVISOR (Gestión operativa)
    supervisor_group, created = Group.objects.get_or_create(name='Supervisores')
    if created:
        print("Grupo 'Supervisores' creado")
    
    permisos_supervisor = [
        # Usuario (solo ver)
        'usuario.view_usuario',
        # Farmacia (ver y editar)
        'farmacia.view_farmacia', 'farmacia.change_farmacia',
        # Motorista (ver y editar)
        'motorista.view_motorista', 'motorista.change_motorista',
        # Moto (ver y editar)
        'moto.view_moto', 'moto.change_moto',
        # Asignación (gestión completa)
        'asignacion.add_asignacionfarmacia', 'asignacion.change_asignacionfarmacia', 'asignacion.delete_asignacionfarmacia', 'asignacion.view_asignacionfarmacia',
        'asignacion.add_asignacionmoto', 'asignacion.change_asignacionmoto', 'asignacion.delete_asignacionmoto', 'asignacion.view_asignacionmoto',
        'asignacion.can_manage_asignaciones',
        # Movimiento (gestión completa)
        'movimiento.add_movimiento', 'movimiento.change_movimiento', 'movimiento.delete_movimiento', 'movimiento.view_movimiento',
        'movimiento.add_movimientodirecto', 'movimiento.change_movimientodirecto', 'movimiento.delete_movimientodirecto', 'movimiento.view_movimientodirecto',
        'movimiento.add_movimientoreceta', 'movimiento.change_movimientoreceta', 'movimiento.delete_movimientoreceta', 'movimiento.view_movimientoreceta',
        'movimiento.add_movimientotraslado', 'movimiento.change_movimientotraslado', 'movimiento.delete_movimientotraslado', 'movimiento.view_movimientotraslado',
        'movimiento.add_movimientoreenvio', 'movimiento.change_movimientoreenvio', 'movimiento.delete_movimientoreenvio', 'movimiento.view_movimientoreenvio',
        'movimiento.add_bitacoramovimiento', 'movimiento.change_bitacoramovimiento', 'movimiento.delete_bitacoramovimiento', 'movimiento.view_bitacoramovimiento',
        'movimiento.add_estadomovimiento', 'movimiento.change_estadomovimiento', 'movimiento.delete_estadomovimiento', 'movimiento.view_estadomovimiento',
        # Reportes (solo ver)
        'reporte.view_configuracionreporte', 'reporte.view_filtroreporte', 'reporte.view_reportegenerado',
        # Configuración (gestión de incidencias)
        'configuracion.view_incidenciamovimiento', 'configuracion.add_incidenciamovimiento', 'configuracion.change_incidenciamovimiento',
    ]
    
    for perm_codename in permisos_supervisor:
        try:
            app_label, codename = perm_codename.split('.')
            perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
            supervisor_group.permissions.add(perm)
        except Permission.DoesNotExist:
            print(f"Permiso no encontrado: {perm_codename}")
    
    print(f"Permisos asignados a Supervisores: {supervisor_group.permissions.count()}")

    # 3. GRUPO OPERADOR (Operaciones básicas)
    operador_group, created = Group.objects.get_or_create(name='Operadores')
    if created:
        print("Grupo 'Operadores' creado")
    
    permisos_operador = [
        # Solo operaciones de movimiento
        'movimiento.add_movimiento', 'movimiento.change_movimiento', 'movimiento.view_movimiento',
        'movimiento.add_movimientodirecto', 'movimiento.change_movimientodirecto', 'movimiento.view_movimientodirecto',
        'movimiento.add_movimientoreceta', 'movimiento.change_movimientoreceta', 'movimiento.view_movimientoreceta',
        'movimiento.add_movimientotraslado', 'movimiento.change_movimientotraslado', 'movimiento.view_movimientotraslado',
        'movimiento.add_movimientoreenvio', 'movimiento.change_movimientoreenvio', 'movimiento.view_movimientoreenvio',
        'movimiento.view_bitacoramovimiento', 'movimiento.view_estadomovimiento',
        # Solo ver farmacias, motoristas y motos
        'farmacia.view_farmacia', 'motorista.view_motorista', 'moto.view_moto',
        # Solo ver asignaciones
        'asignacion.view_asignacionfarmacia', 'asignacion.view_asignacionmoto',
    ]
    
    for perm_codename in permisos_operador:
        try:
            app_label, codename = perm_codename.split('.')
            perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
            operador_group.permissions.add(perm)
        except Permission.DoesNotExist:
            print(f"Permiso no encontrado: {perm_codename}")
    
    print(f"Permisos asignados a Operadores: {operador_group.permissions.count()}")

    # 4. GRUPO MOTORISTA (Acceso limitado)
    motorista_group, created = Group.objects.get_or_create(name='Motoristas')
    if created:
        print("Grupo 'Motoristas' creado")
    
    permisos_motorista = [
        # Solo ver movimientos asignados
        'movimiento.view_movimiento', 'movimiento.view_movimientodirecto', 'movimiento.view_movimientoreceta',
        'movimiento.view_movimientotraslado', 'movimiento.view_movimientoreenvio',
        # Solo cambiar estado de movimientos asignados
        'movimiento.change_movimiento',
        # Ver bitácora propia
        'movimiento.view_bitacoramovimiento',
        # Ver información básica
        'farmacia.view_farmacia', 'motorista.view_motorista', 'moto.view_moto',
    ]
    
    for perm_codename in permisos_motorista:
        try:
            app_label, codename = perm_codename.split('.')
            perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
            motorista_group.permissions.add(perm)
        except Permission.DoesNotExist:
            print(f"Permiso no encontrado: {perm_codename}")
    
    print(f"Permisos asignados a Motoristas: {motorista_group.permissions.count()}")
    
    return {
        'gerente': gerente_group,
        'supervisor': supervisor_group,
        'operador': operador_group,
        'motorista': motorista_group
    }

def crear_usuarios_demo(grupos):
    """Crea usuarios demo para cada rol"""
    
    print("\nCREANDO USUARIOS DEMO")
    
    # Datos de usuarios
    usuarios_data = [
        {
            'username': 'gerente.logico',
            'password': 'LogicoGerente.2025',
            'email': 'gerente@logico.com',
            'first_name': 'Gerente',
            'last_name': 'LogiCo',
            'rol': 'gerente',
            'group': grupos['gerente']
        },
        {
            'username': 'supervisor.logico',
            'password': 'LogicoSupervisor.2025',
            'email': 'supervisor@logico.com',
            'first_name': 'Supervisor',
            'last_name': 'LogiCo',
            'rol': 'supervisor',
            'group': grupos['supervisor']
        },
        {
            'username': 'operador.logico',
            'password': 'LogicoOperador.2025',
            'email': 'operador@logico.com',
            'first_name': 'Operador',
            'last_name': 'LogiCo',
            'rol': 'operador',
            'group': grupos['operador']
        },
        {
            'username': 'motorista.logico',
            'password': 'LogicoMotorista.2025',
            'email': 'motorista@logico.com',
            'first_name': 'Motorista',
            'last_name': 'LogiCo',
            'rol': 'motorista',
            'group': grupos['motorista']
        }
    ]
    
    for user_data in usuarios_data:
        # Verificar si el usuario ya existe
        if User.objects.filter(username=user_data['username']).exists():
            user = User.objects.get(username=user_data['username'])
            print(f"Usuario {user_data['username']} ya existe, actualizando...")
        else:
            # Crear nuevo usuario
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                rol=user_data['rol']
            )
            print(f"Usuario {user_data['username']} creado")
        
        # Asignar grupo
        user.groups.add(user_data['group'])
        user.save()
        
        print(f"Usuario: {user.username}")
        print(f"Email: {user.email}")
        print(f"Rol: {user.rol}")
        print(f"Grupo: {user_data['group'].name}")
        print(f"Password: {user_data['password']}")
        print()

def verificar_creacion():
    """Verifica que todo se creó correctamente"""
    
    print("\nVERIFICACION FINAL")
    
    # Verificar grupos
    grupos = Group.objects.all()
    print("Grupos creados:")
    for grupo in grupos:
        print(f"- {grupo.name}: {grupo.permissions.count()} permisos")
    
    # Verificar usuarios
    usuarios = User.objects.all()
    print("\nUsuarios creados:")
    for usuario in usuarios:
        grupos_usuario = [g.name for g in usuario.groups.all()]
        print(f"- {usuario.username} ({usuario.rol}): {grupos_usuario}")
    
    print(f"\nTotal usuarios: {usuarios.count()}")
    print(f"Total grupos: {grupos.count()}")

if __name__ == "__main__":
    print("INICIANDO CREACION DE USUARIOS Y GRUPOS LOGICO")
    print("=" * 50)
    
    try:
        # Crear grupos y permisos
        grupos = crear_grupos_y_permisos()
        
        # Crear usuarios demo
        crear_usuarios_demo(grupos)
        
        # Verificar creación
        verificar_creacion()
        
        print("\nPROCESO COMPLETADO EXITOSAMENTE")
        print("\nCREDENCIALES DE ACCESO:")
        print("Gerente:     gerente.logico / LogicoGerente.2025")
        print("Supervisor:  supervisor.logico / LogicoSupervisor.2025")
        print("Operador:    operador.logico / LogicoOperador.2025")
        print("Motorista:   motorista.logico / LogicoMotorista.2025")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
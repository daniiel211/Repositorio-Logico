"""
Script para crear usuarios, grupos y asignar permisos en el sistema LogiCo
Incluye todos los permisos actualizados del sistema basados en la lista de permisos
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
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

def crear_grupos_y_permisos():
    """Crea los grupos y asigna permisos según los roles del sistema"""
    
    print("CREANDO GRUPOS Y PERMISOS")
    
    # 1. GRUPO GERENTE - Acceso total a todo el sistema
    gerente_group, created = Group.objects.get_or_create(name='Gerentes')
    if created:
        print("Grupo 'Gerentes' creado")
    
    # Permisos completos para Gerente (todas las apps)
    permisos_gerente = [
        # Admin
        'add_logentry', 'change_logentry', 'delete_logentry', 'view_logentry',
        
        # Asignacion
        'add_asignacionfarmacia', 'change_asignacionfarmacia', 'delete_asignacionfarmacia', 'view_asignacionfarmacia',
        'add_asignacionmoto', 'change_asignacionmoto', 'delete_asignacionmoto', 'view_asignacionmoto',
        'can_manage_asignaciones',
        
        # Auth
        'add_group', 'change_group', 'delete_group', 'view_group',
        'add_permission', 'change_permission', 'delete_permission', 'view_permission',
        
        # Configuracion
        'add_configuracionsistema', 'change_configuracionsistema', 'delete_configuracionsistema', 'view_configuracionsistema',
        'add_incidenciamovimiento', 'change_incidenciamovimiento', 'delete_incidenciamovimiento', 'view_incidenciamovimiento',
        'add_rangoaccion', 'change_rangoaccion', 'delete_rangoaccion', 'view_rangoaccion',
        'add_tipoincidencia', 'change_tipoincidencia', 'delete_tipoincidencia', 'view_tipoincidencia',
        
        # Contenttypes
        'add_contenttype', 'change_contenttype', 'delete_contenttype', 'view_contenttype',
        
        # Farmacia
        'add_farmacia', 'change_farmacia', 'delete_farmacia', 'view_farmacia',
        
        # Moto
        'add_moto', 'change_moto', 'delete_moto', 'view_moto',
        
        # Motorista
        'add_motorista', 'change_motorista', 'delete_motorista', 'view_motorista',
        
        # Movimiento
        'add_bitacoramovimiento', 'change_bitacoramovimiento', 'delete_bitacoramovimiento', 'view_bitacoramovimiento',
        'add_movimiento', 'change_movimiento', 'delete_movimiento', 'view_movimiento',
        'add_movimientodirecto', 'change_movimientodirecto', 'delete_movimientodirecto', 'view_movimientodirecto',
        'add_movimientoreceta', 'change_movimientoreceta', 'delete_movimientoreceta', 'view_movimientoreceta',
        'add_movimientoreenvio', 'change_movimientoreenvio', 'delete_movimientoreenvio', 'view_movimientoreenvio',
        'add_movimientotraslado', 'change_movimientotraslado', 'delete_movimientotraslado', 'view_movimientotraslado',
        'add_ordendespacho', 'change_ordendespacho', 'delete_ordendespacho', 'view_ordendespacho',
        
        # Reporte
        'add_configuracionreporte', 'change_configuracionreporte', 'delete_configuracionreporte', 'view_configuracionreporte',
        'add_filtroreporte', 'change_filtroreporte', 'delete_filtroreporte', 'view_filtroreporte',
        'add_reportegenerado', 'change_reportegenerado', 'delete_reportegenerado', 'view_reportegenerado',
        'view_reporte', 'view_reporte_gerencial',
        
        # Sessions
        'add_session', 'change_session', 'delete_session', 'view_session',
        
        # Usuario
        'add_usuario', 'change_usuario', 'delete_usuario', 'view_usuario',
    ]
    
    # Asignar permisos al grupo Gerente
    permisos_asignados = 0
    for perm_codename in permisos_gerente:
        try:
            perm = Permission.objects.get(codename=perm_codename)
            gerente_group.permissions.add(perm)
            permisos_asignados += 1
        except Permission.DoesNotExist:
            print(f"Permiso no encontrado: {perm_codename}")
    
    print(f"Permisos asignados a Gerentes: {permisos_asignados}")

    # 2. GRUPO SUPERVISOR - Gestión operativa sin permisos de eliminación crítica
    supervisor_group, created = Group.objects.get_or_create(name='Supervisores')
    if created:
        print("Grupo 'Supervisores' creado")
    
    permisos_supervisor = [
        # Asignacion (sin eliminar)
        'add_asignacionfarmacia', 'change_asignacionfarmacia', 'view_asignacionfarmacia',
        'add_asignacionmoto', 'change_asignacionmoto', 'view_asignacionmoto',
        'can_manage_asignaciones',
        
        # Auth (solo ver grupos)
        'view_group', 'view_permission',
        
        # Configuracion (solo ver y cambiar, no eliminar)
        'change_configuracionsistema', 'view_configuracionsistema',
        'add_incidenciamovimiento', 'change_incidenciamovimiento', 'view_incidenciamovimiento',
        'add_rangoaccion', 'change_rangoaccion', 'view_rangoaccion',
        'add_tipoincidencia', 'change_tipoincidencia', 'view_tipoincidencia',
        
        # Farmacia (sin eliminar)
        'add_farmacia', 'change_farmacia', 'view_farmacia',
        
        # Moto (sin eliminar)
        'add_moto', 'change_moto', 'view_moto',
        
        # Motorista (sin eliminar)
        'add_motorista', 'change_motorista', 'view_motorista',
        
        # Movimiento (sin eliminar)
        'view_bitacoramovimiento',
        'add_movimiento', 'change_movimiento', 'view_movimiento',
        'add_movimientodirecto', 'change_movimientodirecto', 'view_movimientodirecto',
        'add_movimientoreceta', 'change_movimientoreceta', 'view_movimientoreceta',
        'add_movimientoreenvio', 'change_movimientoreenvio', 'view_movimientoreenvio',
        'add_movimientotraslado', 'change_movimientotraslado', 'view_movimientotraslado',
        'add_ordendespacho', 'change_ordendespacho', 'view_ordendespacho',
        
        # Reporte (solo ver)
        'view_configuracionreporte',
        'view_filtroreporte',
        'view_reportegenerado', 'view_reporte',
        
        # Usuario (sin eliminar)
        'add_usuario', 'change_usuario', 'view_usuario',
    ]
    
    permisos_asignados = 0
    for perm_codename in permisos_supervisor:
        try:
            perm = Permission.objects.get(codename=perm_codename)
            supervisor_group.permissions.add(perm)
            permisos_asignados += 1
        except Permission.DoesNotExist:
            print(f"Permiso no encontrado: {perm_codename}")
    
    print(f"Permisos asignados a Supervisores: {permisos_asignados}")

    # 3. GRUPO OPERADOR - Operaciones básicas, solo crear y ver
    operador_group, created = Group.objects.get_or_create(name='Operadores')
    if created:
        print("Grupo 'Operadores' creado")
    
    permisos_operador = [
        # Asignacion (solo ver)
        'view_asignacionfarmacia', 'view_asignacionmoto',
        
        # Configuracion (solo ver)
        'view_configuracionsistema',
        'view_incidenciamovimiento',
        'view_rangoaccion',
        'view_tipoincidencia',
        
        # Farmacia (solo ver)
        'view_farmacia',
        
        # Moto (solo ver)
        'view_moto',
        
        # Motorista (solo ver)
        'view_motorista',
        
        # Movimiento (solo crear y ver, no editar ni eliminar)
        'view_bitacoramovimiento',
        'add_movimiento', 'view_movimiento',
        'add_movimientodirecto', 'view_movimientodirecto',
        'add_movimientoreceta', 'view_movimientoreceta',
        'add_movimientoreenvio', 'view_movimientoreenvio',
        'add_movimientotraslado', 'view_movimientotraslado',
        'add_ordendespacho', 'view_ordendespacho',
        
        # Reporte (solo ver básicos)
        'view_reportegenerado',
        
        # Usuario (solo ver)
        'view_usuario',
    ]
    
    permisos_asignados = 0
    for perm_codename in permisos_operador:
        try:
            perm = Permission.objects.get(codename=perm_codename)
            operador_group.permissions.add(perm)
            permisos_asignados += 1
        except Permission.DoesNotExist:
            print(f"Permiso no encontrado: {perm_codename}")
    
    print(f"Permisos asignados a Operadores: {permisos_asignados}")

    # 4. GRUPO MOTORISTA - Acceso muy limitado, solo ver información relevante
    motorista_group, created = Group.objects.get_or_create(name='Motoristas')
    if created:
        print("Grupo 'Motoristas' creado")
    
    permisos_motorista = [
        # Asignacion (solo ver propias)
        'view_asignacionfarmacia', 'view_asignacionmoto',
        
        # Farmacia (solo ver)
        'view_farmacia',
        
        # Moto (solo ver asignada)
        'view_moto',
        
        # Motorista (solo ver propio perfil)
        'view_motorista',
        
        # Movimiento (solo ver propios y cambiar estado)
        'view_bitacoramovimiento',
        'view_movimiento', 'change_movimiento',
        'view_movimientodirecto',
        'view_movimientoreceta',
        'view_movimientoreenvio',
        'view_movimientotraslado',
        'view_ordendespacho',
        
        # Usuario (solo ver propio perfil)
        'view_usuario',
    ]
    
    permisos_asignados = 0
    for perm_codename in permisos_motorista:
        try:
            perm = Permission.objects.get(codename=perm_codename)
            motorista_group.permissions.add(perm)
            permisos_asignados += 1
        except Permission.DoesNotExist:
            print(f"Permiso no encontrado: {perm_codename}")
    
    print(f"Permisos asignados a Motoristas: {permisos_asignados}")
    
    return {
        'gerente': gerente_group,
        'supervisor': supervisor_group,
        'operador': operador_group,
        'motorista': motorista_group
    }

def crear_usuarios_demo(grupos):
    """Crea usuarios demo para cada rol con credenciales específicas"""
    
    print("\nCREANDO USUARIOS DEMO")
    
    # Datos de usuarios por rol
    usuarios_data = [
        {
            'username': 'gerente.logico',
            'password': 'GerenteLogico2025!',
            'email': 'gerente@logico.com',
            'first_name': 'Ana',
            'last_name': 'García',
            'rut': '12.345.678-9',
            'telefono': '+56 9 1234 5678',
            'rol': 'gerente',
            'group': grupos['gerente']
        },
        {
            'username': 'supervisor.logico',
            'password': 'SupervisorLogico2025!',
            'email': 'supervisor@logico.com',
            'first_name': 'Carlos',
            'last_name': 'López',
            'rut': '23.456.789-0',
            'telefono': '+56 9 2345 6789',
            'rol': 'supervisor',
            'group': grupos['supervisor']
        },
        {
            'username': 'operador.logico',
            'password': 'OperadorLogico2025!',
            'email': 'operador@logico.com',
            'first_name': 'María',
            'last_name': 'Rodríguez',
            'rut': '34.567.890-1',
            'telefono': '+56 9 3456 7890',
            'rol': 'operador',
            'group': grupos['operador']
        },
        {
            'username': 'motorista.logico',
            'password': 'MotoristaLogico2025!',
            'email': 'motorista@logico.com',
            'first_name': 'Pedro',
            'last_name': 'Martínez',
            'rut': '45.678.901-2',
            'telefono': '+56 9 4567 8901',
            'rol': 'motorista',
            'group': grupos['motorista']
        }
    ]
    
    usuarios_creados = []
    
    for user_data in usuarios_data:
        # Verificar si el usuario ya existe
        if User.objects.filter(username=user_data['username']).exists():
            user = User.objects.get(username=user_data['username'])
            print(f"Usuario {user_data['username']} ya existe, actualizando...")
            
            # Actualizar datos del usuario
            user.email = user_data['email']
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.rut = user_data['rut']
            user.telefono = user_data['telefono']
            user.rol = user_data['rol']
            user.set_password(user_data['password'])
            user.save()
        else:
            # Crear nuevo usuario
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                rut=user_data['rut'],
                telefono=user_data['telefono'],
                rol=user_data['rol']
            )
            print(f"Usuario {user_data['username']} creado")
        
        # Limpiar grupos existentes y asignar nuevo grupo
        user.groups.clear()
        user.groups.add(user_data['group'])
        user.save()
        
        usuarios_creados.append({
            'username': user.username,
            'rol': user.rol,
            'group': user_data['group'].name
        })
        
        print(f"  Usuario: {user.username}")
        print(f"  Rol: {user.rol}")
        print(f"  Grupo: {user_data['group'].name}")
        print("  " + "-" * 30)
    
    return usuarios_creados

def crear_superusuario():
    """Crea un superusuario con acceso total al sistema"""
    
    print("\nCREANDO SUPERUSUARIO")
    
    superuser_data = {
        'username': 'admin.logico',
        'password': 'AdminLogico2025!',
        'email': 'admin@logico.com',
        'first_name': 'Administrador',
        'last_name': 'Sistema',
        'rut': '99.999.999-9',
        'telefono': '+56 9 9999 9999',
        'rol': 'gerente'
    }
    
    if User.objects.filter(username=superuser_data['username']).exists():
        user = User.objects.get(username=superuser_data['username'])
        print(f"Superusuario {superuser_data['username']} ya existe")
    else:
        user = User.objects.create_superuser(
            username=superuser_data['username'],
            email=superuser_data['email'],
            password=superuser_data['password'],
            first_name=superuser_data['first_name'],
            last_name=superuser_data['last_name'],
            rut=superuser_data['rut'],
            telefono=superuser_data['telefono'],
            rol=superuser_data['rol']
        )
        print(f"Superusuario {superuser_data['username']} creado")
    
    # Asignar a todos los grupos
    grupos = Group.objects.all()
    for grupo in grupos:
        user.groups.add(grupo)
    
    user.save()
    
    print(f"  Usuario: {user.username}")
    print(f"  Rol: {user.rol}")
    print(f"  Es superusuario: {user.is_superuser}")
    print("  " + "-" * 30)
    
    return user

def verificar_creacion():
    """Verifica que todo se creó correctamente mostrando un resumen"""
    
    print("\nVERIFICACION FINAL")
    
    # Verificar grupos
    grupos = Group.objects.all()
    print("GRUPOS CREADOS:")
    for grupo in grupos:
        permisos = grupo.permissions.all()
        print(f"- {grupo.name}: {permisos.count()} permisos")
    
    # Verificar usuarios
    usuarios = User.objects.all().order_by('rol')
    print("\nUSUARIOS CREADOS:")
    for usuario in usuarios:
        grupos_usuario = [g.name for g in usuario.groups.all()]
        print(f"- {usuario.username} (Rol: {usuario.rol}) - Grupos: {', '.join(grupos_usuario)}")
    
    print(f"\nRESUMEN:")
    print(f"Total usuarios: {usuarios.count()}")
    print(f"Total grupos: {grupos.count()}")

def mostrar_resumen_permisos():
    """Muestra un resumen detallado de permisos por rol"""
    
    print("\n" + "=" * 80)
    print("RESUMEN DETALLADO DE PERMISOS POR ROL")
    print("=" * 80)
    
    grupos = Group.objects.all()
    
    for grupo in grupos:
        print(f"\n{grupo.name.upper()}")
        print("-" * 40)
        
        permisos = grupo.permissions.all()
        
        # Agrupar permisos por aplicación
        apps_permisos = {}
        for perm in permisos:
            app_label = perm.content_type.app_label
            if app_label not in apps_permisos:
                apps_permisos[app_label] = []
            apps_permisos[app_label].append(perm.codename)
        
        for app, perms in sorted(apps_permisos.items()):
            print(f"\n{app.upper()}:")
            for perm in sorted(perms):
                print(f"  - {perm}")

if __name__ == "__main__":
    print("INICIANDO CREACION DE USUARIOS Y GRUPOS LOGICO")
    print("=" * 80)
    
    try:
        # Fase 1: Crear grupos y permisos
        print("FASE 1: Creando grupos y permisos...")
        grupos = crear_grupos_y_permisos()
        
        # Fase 2: Crear superusuario
        print("\nFASE 2: Creando superusuario...")
        crear_superusuario()
        
        # Fase 3: Crear usuarios demo
        print("\nFASE 3: Creando usuarios demo...")
        usuarios_creados = crear_usuarios_demo(grupos)
        
        # Fase 4: Verificar creación
        print("\nFASE 4: Verificando creación...")
        verificar_creacion()
        
        # Fase 5: Mostrar resumen detallado
        mostrar_resumen_permisos()
        
        print("\n" + "=" * 80)
        print("PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        
        print("\nCREDENCIALES DE ACCESO:")
        print("Superusuario (acceso total):")
        print("  Usuario: admin.logico")
        print("  Password: AdminLogico2025!")
        
        print("\nUsuarios por rol:")
        print("  Gerente (Acceso completo):")
        print("    Usuario: gerente.logico")
        print("    Password: GerenteLogico2025!")
        
        print("  Supervisor (Gestión operativa):")
        print("    Usuario: supervisor.logico")  
        print("    Password: SupervisorLogico2025!")
        
        print("  Operador (Operaciones básicas):")
        print("    Usuario: operador.logico")
        print("    Password: OperadorLogico2025!")
        
        print("  Motorista (Acceso limitado):")
        print("    Usuario: motorista.logico")
        print("    Password: MotoristaLogico2025!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
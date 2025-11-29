"""
Script para crear usuarios, grupos y asignar permisos en el sistema LogiCo
INCLUYE PERMISOS PARA APLICACIONES: USUARIO, FARMACIA, MOTO, MOTORISTA Y ASIGNACION
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
    
    # 1. GRUPO GERENTE (Acceso total)
    gerente_group, created = Group.objects.get_or_create(name='Gerentes')
    if created:
        print("Grupo 'Gerentes' creado")
    
    # Permisos específicos para todas las aplicaciones
    permisos_gerente = [
        # Usuario (acceso completo)
        'add_usuario', 'change_usuario', 'delete_usuario', 'view_usuario',
        # Farmacia (acceso completo)
        'add_farmacia', 'change_farmacia', 'delete_farmacia', 'view_farmacia',
        # Moto (acceso completo)
        'add_moto', 'change_moto', 'delete_moto', 'view_moto',
        # Motorista (acceso completo)
        'add_motorista', 'change_motorista', 'delete_motorista', 'view_motorista',
        # Asignación (acceso completo)
        'add_asignacionmoto', 'change_asignacionmoto', 'delete_asignacionmoto', 'view_asignacionmoto',
        'add_asignacionfarmacia', 'change_asignacionfarmacia', 'delete_asignacionfarmacia', 'view_asignacionfarmacia',
        # Core (acceso completo)
        'view_dashboard', 'view_estadisticas', 'change_configuracionsistema',
    ]
    
    # Asignar permisos al grupo Gerente
    for perm_codename in permisos_gerente:
        try:
            perm = Permission.objects.get(codename=perm_codename)
            gerente_group.permissions.add(perm)
            print(f"Permiso asignado a Gerentes: {perm_codename}")
        except Permission.DoesNotExist:
            print(f"Permiso no encontrado: {perm_codename}")
    
    print(f"Permisos asignados a Gerentes: {gerente_group.permissions.count()}")

    # 2. GRUPO SUPERVISOR (Gestión operativa)
    supervisor_group, created = Group.objects.get_or_create(name='Supervisores')
    if created:
        print("Grupo 'Supervisores' creado")
    
    permisos_supervisor = [
        # Usuario (ver y editar)
        'change_usuario', 'view_usuario',
        # Farmacia (ver y editar)
        'change_farmacia', 'view_farmacia',
        # Moto (ver y editar)
        'change_moto', 'view_moto',
        # Motorista (ver y editar)
        'change_motorista', 'view_motorista',
        # Asignación (ver y editar)
        'add_asignacionmoto', 'change_asignacionmoto', 'view_asignacionmoto',
        'add_asignacionfarmacia', 'change_asignacionfarmacia', 'view_asignacionfarmacia',
        # Core (vista limitada)
        'view_dashboard', 'view_estadisticas',
    ]
    
    for perm_codename in permisos_supervisor:
        try:
            perm = Permission.objects.get(codename=perm_codename)
            supervisor_group.permissions.add(perm)
            print(f"Permiso asignado a Supervisores: {perm_codename}")
        except Permission.DoesNotExist:
            print(f"Permiso no encontrado: {perm_codename}")
    
    print(f"Permisos asignados a Supervisores: {supervisor_group.permissions.count()}")

    # 3. GRUPO OPERADOR (Operaciones básicas)
    operador_group, created = Group.objects.get_or_create(name='Operadores')
    if created:
        print("Grupo 'Operadores' creado")
    
    permisos_operador = [
        # Usuario (solo ver)
        'view_usuario',
        # Farmacia (solo ver)
        'view_farmacia',
        # Moto (solo ver)
        'view_moto',
        # Motorista (solo ver)
        'view_motorista',
        # Asignación (solo ver)
        'view_asignacionmoto', 'view_asignacionfarmacia',
        # Core (solo dashboard)
        'view_dashboard',
    ]
    
    for perm_codename in permisos_operador:
        try:
            perm = Permission.objects.get(codename=perm_codename)
            operador_group.permissions.add(perm)
            print(f"Permiso asignado a Operadores: {perm_codename}")
        except Permission.DoesNotExist:
            print(f"Permiso no encontrado: {perm_codename}")
    
    print(f"Permisos asignados a Operadores: {operador_group.permissions.count()}")

    # 4. GRUPO MOTORISTA (Acceso limitado)
    motorista_group, created = Group.objects.get_or_create(name='Motoristas')
    if created:
        print("Grupo 'Motoristas' creado")
    
    permisos_motorista = [
        # Usuario (solo ver propio perfil)
        'view_usuario',
        # Farmacia (solo ver)
        'view_farmacia',
        # Moto (solo ver)
        'view_moto',
        # Motorista (solo ver propio perfil)
        'view_motorista',
        # Asignación (solo ver propias asignaciones)
        'view_asignacionmoto', 'view_asignacionfarmacia',
        # Core (solo dashboard básico)
        'view_dashboard',
    ]
    
    for perm_codename in permisos_motorista:
        try:
            perm = Permission.objects.get(codename=perm_codename)
            motorista_group.permissions.add(perm)
            print(f"Permiso asignado a Motoristas: {perm_codename}")
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
            'first_name': 'Ana',
            'last_name': 'García',
            'rut': '12.345.678-9',
            'telefono': '+56 9 1234 5678',
            'rol': 'gerente',
            'group': grupos['gerente']
        },
        {
            'username': 'supervisor.logico',
            'password': 'LogicoSupervisor.2025',
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
            'password': 'LogicoOperador.2025',
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
            'password': 'LogicoMotorista.2025',
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
            
            # Actualizar datos
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
        
        print(f"Usuario: {user.username}")
        print(f"Email: {user.email}")
        print(f"Nombre: {user.get_full_name()}")
        print(f"RUT: {user.rut}")
        print(f"Teléfono: {user.telefono}")
        print(f"Rol: {user.rol}")
        print(f"Grupo: {user_data['group'].name}")
        print(f"Password: {user_data['password']}")
        print("-" * 40)
    
    return usuarios_creados

def crear_superusuario():
    """Crea un superusuario para administración total"""
    
    print("\nCREANDO SUPERUSUARIO")
    
    superuser_data = {
        'username': 'admin.logico',
        'password': 'AdminLogico.2025',
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
    
    print(f"Superusuario: {user.username}")
    print(f"Email: {user.email}")
    print(f"Nombre: {user.get_full_name()}")
    print(f"Rol: {user.rol}")
    print(f"Es superusuario: {user.is_superuser}")
    print(f"Grupos: {[g.name for g in user.groups.all()]}")
    print(f"Password: {superuser_data['password']}")
    print("-" * 40)
    
    return user

def verificar_creacion():
    """Verifica que todo se creó correctamente"""
    
    print("\nVERIFICACION FINAL")
    
    # Verificar grupos
    grupos = Group.objects.all()
    print("GRUPOS CREADOS:")
    for grupo in grupos:
        permisos = grupo.permissions.all()
        print(f"- {grupo.name}: {permisos.count()} permisos")
        
        # Mostrar permisos por aplicación
        for app_label in ['usuario', 'farmacia', 'moto', 'motorista', 'asignacion', 'core']:
            permisos_app = permisos.filter(content_type__app_label=app_label)
            if permisos_app:
                print(f"  {app_label.capitalize()}: {permisos_app.count()} permisos")
    
    # Verificar usuarios
    usuarios = User.objects.all().order_by('rol')
    print("\nUSUARIOS CREADOS:")
    for usuario in usuarios:
        grupos_usuario = [g.name for g in usuario.groups.all()]
        print(f"- {usuario.username}")
        print(f"  Rol: {usuario.rol}")
        print(f"  Nombre: {usuario.get_full_name()}")
        print(f"  Email: {usuario.email}")
        print(f"  Grupos: {', '.join(grupos_usuario)}")
        print(f"  Activo: {usuario.is_active}")
        print(f"  Superusuario: {usuario.is_superuser}")
        print()
    
    print(f"RESUMEN:")
    print(f"Total usuarios: {usuarios.count()}")
    print(f"Total grupos: {grupos.count()}")

def mostrar_resumen_permisos():
    """Muestra un resumen detallado de permisos por rol"""
    
    print("\n" + "=" * 80)
    print("RESUMEN DETALLADO DE PERMISOS POR ROL")
    print("=" * 80)
    
    grupos = Group.objects.all()
    
    for grupo in grupos:
        print(f"\n📋 {grupo.name.upper()}")
        print("-" * 40)
        
        permisos = grupo.permissions.all()
        
        # Permisos por aplicación
        apps_permisos = {}
        for perm in permisos:
            app_label = perm.content_type.app_label
            if app_label not in apps_permisos:
                apps_permisos[app_label] = []
            apps_permisos[app_label].append(perm.codename)
        
        for app, perms in apps_permisos.items():
            print(f"\n📁 {app.upper()}:")
            for perm in sorted(perms):
                print(f"  ✅ {perm}")

if __name__ == "__main__":
    print("INICIANDO CREACION DE USUARIOS Y GRUPOS LOGICO")
    print("INCLUYENDO PERMISOS DE: USUARIO, FARMACIA, MOTO, MOTORISTA Y ASIGNACION")
    print("=" * 80)
    
    try:
        # Crear grupos y permisos
        print("FASE 1: Creando grupos y permisos...")
        grupos = crear_grupos_y_permisos()
        
        # Crear superusuario
        print("\nFASE 2: Creando superusuario...")
        crear_superusuario()
        
        # Crear usuarios demo
        print("\nFASE 3: Creando usuarios demo...")
        usuarios_creados = crear_usuarios_demo(grupos)
        
        # Verificar creación
        print("\nFASE 4: Verificando creación...")
        verificar_creacion()
        
        # Mostrar resumen detallado
        mostrar_resumen_permisos()
        
        print("\n" + "=" * 80)
        print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        
        print("\n🔐 CREDENCIALES DE ACCESO:")
        print("Superusuario (acceso total):")
        print("  👤 Usuario: admin.logico")
        print("  🔑 Password: AdminLogico.2025")
        
        print("\n👥 Usuarios por rol:")
        print("  🎯 Gerente (Acceso completo):")
        print("    👤 Usuario: gerente.logico")
        print("    🔑 Password: LogicoGerente.2025")
        
        print("  📊 Supervisor (Gestión operativa):")
        print("    👤 Usuario: supervisor.logico")  
        print("    🔑 Password: LogicoSupervisor.2025")
        
        print("  ⚙️  Operador (Operaciones básicas):")
        print("    👤 Usuario: operador.logico")
        print("    🔑 Password: LogicoOperador.2025")
        
        print("  🛵 Motorista (Acceso limitado):")
        print("    👤 Usuario: motorista.logico")
        print("    🔑 Password: LogicoMotorista.2025")
        
        print("\n📋 PERMISOS POR ROL - ASIGNACIONES:")
        print("  🎯 Gerente:")
        print("    ✅ Crear asignaciones: PERMITIDO")
        print("    ✅ Editar asignaciones: PERMITIDO") 
        print("    ✅ Eliminar asignaciones: PERMITIDO")
        print("    ✅ Ver asignaciones: PERMITIDO")
        print("    ✅ Reemplazar motoristas: PERMITIDO")
        
        print("  📊 Supervisor:")
        print("    ✅ Crear asignaciones: PERMITIDO")
        print("    ✅ Editar asignaciones: PERMITIDO")
        print("    ❌ Eliminar asignaciones: DENEGADO") 
        print("    ✅ Ver asignaciones: PERMITIDO")
        print("    ✅ Reemplazar motoristas: PERMITIDO")
        
        print("  ⚙️  Operador:")
        print("    ❌ Crear asignaciones: DENEGADO")
        print("    ❌ Editar asignaciones: DENEGADO")
        print("    ❌ Eliminar asignaciones: DENEGADO")
        print("    ✅ Ver asignaciones: PERMITIDO")
        print("    ❌ Reemplazar motoristas: DENEGADO")
        
        print("  🛵 Motorista:")
        print("    ❌ Crear asignaciones: DENEGADO")
        print("    ❌ Editar asignaciones: DENEGADO")
        print("    ❌ Eliminar asignaciones: DENEGADO")
        print("    👁️  Ver asignaciones: SOLO PROPIAS")
        print("    ❌ Reemplazar motoristas: DENEGADO")
        
        print("\n🔒 PERMISOS POR ROL - USUARIOS:")
        print("  🎯 Gerente:")
        print("    ✅ Crear usuarios: PERMITIDO")
        print("    ✅ Editar usuarios: PERMITIDO") 
        print("    ✅ Eliminar usuarios: PERMITIDO")
        print("    ✅ Ver usuarios: PERMITIDO")
        
        print("  📊 Supervisor:")
        print("    ❌ Crear usuarios: DENEGADO")
        print("    ✅ Editar usuarios: PERMITIDO")
        print("    ❌ Eliminar usuarios: DENEGADO") 
        print("    ✅ Ver usuarios: PERMITIDO")
        
        print("  ⚙️  Operador:")
        print("    ❌ Crear usuarios: DENEGADO")
        print("    ❌ Editar usuarios: DENEGADO")
        print("    ❌ Eliminar usuarios: DENEGADO")
        print("    ✅ Ver usuarios: PERMITIDO")
        
        print("  🛵 Motorista:")
        print("    ❌ Crear usuarios: DENEGADO")
        print("    ❌ Editar usuarios: DENEGADO")
        print("    ❌ Eliminar usuarios: DENEGADO")
        print("    👁️  Ver usuarios: SOLO PROPIO PERFIL")
        
        print("\n💡 NOTA IMPORTANTE:")
        print("  • Los permisos se aplican automáticamente al sistema de control de acceso.")
        print("  • Los botones y enlaces se mostrarán/ocultarán según los permisos de cada usuario.")
        print("  • El middleware de seguridad bloquea accesos no autorizados.")
        print("  • Los motoristas solo pueden ver sus propias asignaciones y perfil.")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
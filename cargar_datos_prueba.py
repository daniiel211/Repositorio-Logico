"""
Script para cargar datos de prueba en el sistema LogiCo
Incluye: farmacias, motos, motoristas, asignaciones y movimientos
Requisitos: Un motorista debe tener asignada una moto para ser asignado a una farmacia
Ejecutar: python manage.py shell < cargar_datos_prueba.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LogiCo_.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.farmacia.models import Farmacia
from apps.moto.models import Moto
from apps.motorista.models import Motorista
from apps.asignacion.models import AsignacionMoto, AsignacionFarmacia
from apps.movimiento.models import Movimiento, MovimientoDirecto, MovimientoReceta
from apps.configuracion.models import ConfiguracionSistema, RangoAccion as ConfiguracionRangoAccion, TipoIncidencia as ConfiguracionTipoIncidencia
from apps.reporte.models import ConfiguracionReporte

User = get_user_model()

def crear_configuraciones_basicas():
    """Crear configuraciones básicas del sistema si no existen"""
    print("Configurando parámetros básicos del sistema...")
    
    # Configuraciones del sistema
    configuraciones = [
        {
            'clave': 'TIEMPO_MAXIMO_ENTREGA',
            'valor': '60',
            'tipo': 'NUMERO',
            'descripcion': 'Tiempo máximo en minutos para completar una entrega',
            'editable': True
        },
        {
            'clave': 'RADIO_COBERTURA',
            'valor': '10',
            'tipo': 'NUMERO',
            'descripcion': 'Distancia máxima en km para asignaciones',
            'editable': True
        },
        {
            'clave': 'HORARIO_OPERACION_INICIO',
            'valor': '08:00',
            'tipo': 'TEXTO',
            'descripcion': 'Horario de inicio de operaciones',
            'editable': True
        },
        {
            'clave': 'HORARIO_OPERACION_FIN',
            'valor': '22:00',
            'tipo': 'TEXTO',
            'descripcion': 'Horario de fin de operaciones',
            'editable': True
        },
        {
            'clave': 'PRIORIDAD_ALTA',
            'valor': '3',
            'tipo': 'NUMERO',
            'descripcion': 'Nivel de prioridad alta para movimientos',
            'editable': True
        },
    ]
    
    for config_data in configuraciones:
        ConfiguracionSistema.objects.get_or_create(
            clave=config_data['clave'],
            defaults=config_data
        )
    
    # Tipos de incidencias
    tipos_incidencia = [
        {
            'codigo': 'RET-001',
            'nombre': 'Retraso en entrega',
            'descripcion': 'El motorista no llegó en el tiempo estimado',
            'gravedad': 'MEDIA',
            'requiere_autorizacion': False,
            'activo': True
        },
        {
            'codigo': 'CLI-002',
            'nombre': 'Cliente no encontrado',
            'descripcion': 'No se encontró al cliente en la dirección especificada',
            'gravedad': 'BAJA',
            'requiere_autorizacion': False,
            'activo': True
        },
        {
            'codigo': 'PRO-003',
            'nombre': 'Producto incorrecto',
            'descripcion': 'Se entregó un producto diferente al solicitado',
            'gravedad': 'ALTA',
            'requiere_autorizacion': True,
            'activo': True
        },
    ]
    
    for tipo_data in tipos_incidencia:
        ConfiguracionTipoIncidencia.objects.get_or_create(
            codigo=tipo_data['codigo'],
            defaults=tipo_data
        )
    
    print("Configuraciones básicas creadas ✓")

def crear_farmacias():
    """Crear 5 farmacias de prueba"""
    print("\nCreando farmacias de prueba...")
    
    farmacias_data = [
        {
            'IdFarmacia': 'FARM-001',
            'nombre': 'Cruz Verde Providencia',
            'direccion': 'Av. Providencia 1234',
            'comuna': 'Providencia',
            'provincia': 'Santiago',
            'region': 'Metropolitana',
            'apertura': '08:00',
            'cierre': '22:00',
            'telefono': '+56 2 2345 6789',
            'latitud': -33.432000,
            'longitud': -70.614000,
            'activo': True
        },
        {
            'IdFarmacia': 'FARM-002',
            'nombre': 'Cruz Verde Las Condes',
            'direccion': 'Av. Apoquindo 4567',
            'comuna': 'Las Condes',
            'provincia': 'Santiago',
            'region': 'Metropolitana',
            'apertura': '08:00',
            'cierre': '22:00',
            'telefono': '+56 2 3456 7890',
            'latitud': -33.415000,
            'longitud': -70.572000,
            'activo': True
        },
        {
            'IdFarmacia': 'FARM-003',
            'nombre': 'Cruz Verde Ñuñoa',
            'direccion': 'Irarrázaval 7890',
            'comuna': 'Ñuñoa',
            'provincia': 'Santiago',
            'region': 'Metropolitana',
            'apertura': '09:00',
            'cierre': '21:00',
            'telefono': '+56 2 4567 8901',
            'latitud': -33.457000,
            'longitud': -70.589000,
            'activo': True
        },
        {
            'IdFarmacia': 'FARM-004',
            'nombre': 'Cruz Verde Maipú',
            'direccion': 'Av. Pajaritos 123',
            'comuna': 'Maipú',
            'provincia': 'Santiago',
            'region': 'Metropolitana',
            'apertura': '08:30',
            'cierre': '21:30',
            'telefono': '+56 2 5678 9012',
            'latitud': -33.511000,
            'longitud': -70.762000,
            'activo': True
        },
        {
            'IdFarmacia': 'FARM-005',
            'nombre': 'Cruz Verde La Florida',
            'direccion': 'Av. La Florida 456',
            'comuna': 'La Florida',
            'provincia': 'Santiago',
            'region': 'Metropolitana',
            'apertura': '08:00',
            'cierre': '22:00',
            'telefono': '+56 2 6789 0123',
            'latitud': -33.522000,
            'longitud': -70.579000,
            'activo': True
        }
    ]
    
    # Obtener usuario administrador para campos de auditoría
    try:
        admin_user = User.objects.get(username='admin.logico')
    except User.DoesNotExist:
        admin_user = User.objects.filter(is_superuser=True).first()
    
    farmacias = []
    for data in farmacias_data:
        # Verificar si la farmacia ya existe
        farmacia, created = Farmacia.objects.get_or_create(
            IdFarmacia=data['IdFarmacia'],
            defaults={
                'nombre': data['nombre'],
                'direccion': data['direccion'],
                'comuna': data['comuna'],
                'provincia': data['provincia'],
                'region': data['region'],
                'apertura': data['apertura'],
                'cierre': data['cierre'],
                'telefono': data['telefono'],
                'latitud': data['latitud'],
                'longitud': data['longitud'],
                'activo': data['activo'],
                'creado_por': admin_user,
                'fecha_creacion': timezone.now(),
                'fecha_modificacion': timezone.now()
            }
        )
        
        if created:
            # Crear rango de acción para la farmacia
            ConfiguracionRangoAccion.objects.create(
                farmacia=farmacia,
                distancia_maxima_km=10.00,
                comunas_permitidas=data['comuna'],
                horario_inicio=data['apertura'],
                horario_fin=data['cierre'],
                activo=True,
                creado_por=admin_user,
                fecha_creacion=timezone.now(),
                fecha_modificacion=timezone.now()
            )
            print(f"Farmacia {data['IdFarmacia']} creada ✓")
        else:
            print(f"Farmacia {data['IdFarmacia']} ya existe")
        
        farmacias.append(farmacia)
    
    return farmacias

def crear_motos():
    """Crear 10 motos de prueba"""
    print("\nCreando motos de prueba...")
    
    marcas_modelos = [
        ('Yamaha', 'YZF-R3', 2022),
        ('Honda', 'CBR500R', 2023),
        ('Kawasaki', 'Ninja 400', 2022),
        ('Suzuki', 'GSX-R150', 2023),
        ('BMW', 'G310R', 2022),
        ('KTM', 'Duke 390', 2023),
        ('Ducati', 'Monster', 2021),
        ('Harley-Davidson', 'Street 750', 2020),
        ('Triumph', 'Street Triple', 2022),
        ('Aprilia', 'RS 660', 2023),
    ]
    
    colores = ['Rojo', 'Azul', 'Negro', 'Blanco', 'Verde', 'Amarillo', 'Gris', 'Naranja']
    
    # Obtener usuario administrador
    try:
        admin_user = User.objects.get(username='admin.logico')
    except User.DoesNotExist:
        admin_user = User.objects.filter(is_superuser=True).first()
    
    motos = []
    for i in range(1, 11):
        marca, modelo, año = marcas_modelos[i-1]
        patente = f'AB{str(i).zfill(2)}CD'
        num_chasis = f'CHASIS-{str(i).zfill(3)}'
        motor = f'MOTOR-{str(i).zfill(3)}'
        
        moto, created = Moto.objects.get_or_create(
            patente=patente,
            defaults={
                'marca': marca,
                'modelo': modelo,
                'año': año,
                'color': random.choice(colores),
                'numChasis': num_chasis,
                'motor': motor,
                'propietario': 'Discopro Ltda.',
                'permisoCirculacion': f'PC-{str(i).zfill(4)}',
                'seguro': f'SEGURO-{str(i).zfill(4)}',
                'revisionTecnica': f'RT-{str(i).zfill(4)}',
                'activo': True,
                'creado_por': admin_user,
                'fecha_creacion': timezone.now(),
                'fecha_modificacion': timezone.now()
            }
        )
        
        if created:
            print(f"Moto {patente} ({marca} {modelo}) creada ✓")
        else:
            print(f"Moto {patente} ya existe")
        
        motos.append(moto)
    
    return motos

def crear_motoristas():
    """Crear 10 motoristas de prueba"""
    print("\nCreando motoristas de prueba...")
    
    nombres = [
        ('Juan', 'Pérez', 'García'),
        ('María', 'López', 'Rodríguez'),
        ('Carlos', 'González', 'Fernández'),
        ('Ana', 'Martínez', 'Sánchez'),
        ('Pedro', 'Hernández', 'Díaz'),
        ('Laura', 'Gómez', 'Moreno'),
        ('Diego', 'Ruiz', 'Jiménez'),
        ('Sofía', 'Torres', 'Navarro'),
        ('Javier', 'Ramírez', 'Castro'),
        ('Elena', 'Romero', 'Ortega'),
    ]
    
    comunas = ['Providencia', 'Las Condes', 'Ñuñoa', 'Maipú', 'La Florida', 'Santiago', 'Vitacura', 'Lo Barnechea']
    
    # Obtener usuario administrador
    try:
        admin_user = User.objects.get(username='admin.logico')
    except User.DoesNotExist:
        admin_user = User.objects.filter(is_superuser=True).first()
    
    motoristas = []
    for i in range(1, 11):
        nombre, apellido_paterno, apellido_materno = nombres[i-1]
        rut = f'{str(15000000 + i)}-{random.randint(0, 9)}'
        
        # Fechas aleatorias
        fecha_nacimiento = datetime.now() - timedelta(days=random.randint(7300, 14600))  # 20-40 años
        fecha_control = datetime.now() - timedelta(days=random.randint(1, 30))
        fecha_vencimiento = fecha_control + timedelta(days=365)
        
        motorista, created = Motorista.objects.get_or_create(
            rut=rut,
            defaults={
                'nombre': nombre,
                'apellidoPaterno': apellido_paterno,
                'apellidoMaterno': apellido_materno,
                'fechaNacimiento': fecha_nacimiento.date(),
                'direccion': f'Calle {i} #123',
                'comuna': random.choice(comunas),
                'provincia': 'Santiago',
                'region': 'Metropolitana',
                'telefono': f'+56 9 {random.randint(1000, 9999)} {random.randint(1000, 9999)}',
                'correo': f'{nombre.lower()}.{apellido_paterno.lower()}@logico.com',
                'moto': 'SI' if i <= 8 else 'NO',  # Los primeros 8 tienen moto
                'archivo': f'CV-{str(i).zfill(3)}.pdf',
                'fechaUltControl': fecha_control.date(),
                'fechaControl': fecha_control.date(),
                'fechaVencimiento': fecha_vencimiento.date(),
                'parentesco': 'Madre' if random.choice([True, False]) else 'Padre',
                'telefonoEmergencia': f'+56 9 {random.randint(1000, 9999)} {random.randint(1000, 9999)}',
                'nombreContacto': f'Contacto {nombre}',
                'apellidoContacto': apellido_paterno,
                'direccionContacto': f'Calle Emergencia {i} #456',
                'activo': True,
                'creado_por': admin_user,
                'fecha_creacion': timezone.now(),
                'fecha_modificacion': timezone.now()
            }
        )
        
        if created:
            print(f"Motorista {rut} ({nombre} {apellido_paterno}) creado ✓")
        else:
            print(f"Motorista {rut} ya existe")
        
        motoristas.append(motorista)
    
    return motoristas

def crear_asignaciones_motos(motos, motoristas):
    """Crear asignaciones de motos a motoristas"""
    print("\nCreando asignaciones de motos...")
    
    # Los primeros 8 motoristas reciben motos (2 motos quedan sin asignar para pruebas)
    asignaciones = []
    for i in range(8):
        moto = motos[i]
        motorista = motoristas[i]
        
        # Verificar si ya existe una asignación activa para este motorista
        existe_asignacion = AsignacionMoto.objects.filter(
            motorista=motorista,
            estado='ACTIVA',
            activo=True
        ).exists()
        
        if not existe_asignacion:
            asignacion = AsignacionMoto.objects.create(
                estado='ACTIVA',
                observaciones=f'Asignación inicial para {motorista.nombre}',
                fecha_asignacion=timezone.now() - timedelta(days=random.randint(1, 30)),
                fecha_finalizacion=None,
                activo=True,
                fecha_creacion=timezone.now(),
                fecha_modificacion=timezone.now(),
                creado_por=motorista.creado_por,
                moto=moto,
                motorista=motorista
            )
            asignaciones.append(asignacion)
            print(f"Asignación moto {moto.patente} → Motorista {motorista.rut} creada ✓")
        else:
            print(f"Motorista {motorista.rut} ya tiene una moto asignada")
    
    return asignaciones

def crear_asignaciones_farmacias(farmacias, motoristas, asignaciones_motos):
    """Crear asignaciones de motoristas a farmacias"""
    print("\nCreando asignaciones a farmacias...")
    
    # Solo asignar motoristas que tengan moto asignada
    motoristas_con_moto = []
    for asignacion in asignaciones_motos:
        motoristas_con_moto.append(asignacion.motorista)
    
    # Verificar que hay motoristas con moto
    if not motoristas_con_moto:
        print("No hay motoristas con moto asignada. No se pueden crear asignaciones a farmacias.")
        return []
    
    asignaciones = []
    for i, farmacia in enumerate(farmacias):
        # Cada farmacia recibe 2 motoristas
        for j in range(2):
            motorista_idx = (i * 2 + j) % len(motoristas_con_moto) if len(motoristas_con_moto) > 0 else 0
            motorista = motoristas_con_moto[motorista_idx]
            
            # Verificar si ya existe una asignación activa para este motorista
            existe_asignacion = AsignacionFarmacia.objects.filter(
                motorista=motorista,
                estado='ACTIVA',
                activo=True
            ).exists()
            
            if not existe_asignacion:
                asignacion = AsignacionFarmacia.objects.create(
                    estado='ACTIVA',
                    observaciones=f'Asignación a {farmacia.nombre}',
                    fecha_asignacion=timezone.now() - timedelta(days=random.randint(1, 30)),
                    fecha_finalizacion=None,
                    activo=True,
                    fecha_creacion=timezone.now(),
                    fecha_modificacion=timezone.now(),
                    creado_por=motorista.creado_por,
                    farmacia=farmacia,
                    motorista=motorista
                )
                asignaciones.append(asignacion)
                print(f"Asignación farmacia {farmacia.IdFarmacia} → Motorista {motorista.rut} creada ✓")
            else:
                print(f"Motorista {motorista.rut} ya está asignado a una farmacia")
    
    return asignaciones

def crear_movimientos(farmacias, asignaciones_farmacias):
    """Crear 10 movimientos por farmacia realizados por diferentes motoristas asignados"""
    print("\nCreando movimientos de prueba...")
    
    # Obtener usuarios de prueba
    try:
        operador = User.objects.get(username='operador.logico')
    except User.DoesNotExist:
        operador = User.objects.filter(rol='operador').first()
    
    # Estados posibles
    estados = ['PENDIENTE', 'EN_CAMINO', 'ENTREGADO', 'FALLIDO']
    productos = [
        'Paracetamol 500mg',
        'Ibuprofeno 400mg',
        'Amoxicilina 500mg',
        'Omeprazol 20mg',
        'Loratadina 10mg',
        'Metformina 850mg',
        'Atorvastatina 20mg',
        'Losartán 50mg',
        'Salbutamol inhalador',
        'Insulina glargina'
    ]
    
    movimientos_totales = []
    
    for farmacia in farmacias:
        print(f"\nCreando movimientos para {farmacia.nombre}...")
        
        # Obtener motoristas asignados a esta farmacia
        motoristas_asignados = AsignacionFarmacia.objects.filter(
            farmacia=farmacia,
            estado='ACTIVA',
            activo=True
        ).select_related('motorista')
        
        if not motoristas_asignados:
            print(f"  No hay motoristas asignados a {farmacia.nombre}, saltando...")
            continue
        
        for i in range(10):  # 10 movimientos por farmacia
            # Seleccionar un motorista aleatorio asignado a esta farmacia
            asignacion = random.choice(list(motoristas_asignados))
            motorista = asignacion.motorista
            
            # Fechas para el movimiento
            fecha_creacion = timezone.now() - timedelta(days=random.randint(1, 7), hours=random.randint(1, 12))
            
            # Determinar estado y fecha de entrega
            estado = random.choice(estados)
            fecha_entrega = None
            if estado in ['ENTREGADO', 'FALLIDO']:
                fecha_entrega = fecha_creacion + timedelta(minutes=random.randint(15, 90))
            
            # Crear movimiento base - TODO CAMELCASE
            movimiento = Movimiento.objects.create(
                tipoMovimiento=random.choice(['DIRECTO', 'RECETA']),
                estado=estado,
                fechaCreacion=fecha_creacion,
                fechaEntrega=fecha_entrega,
                direccionDestino=f'Calle Cliente {i+1} #{random.randint(100, 999)}',
                clienteNombre=f'Cliente {farmacia.comuna} {i+1}',
                clienteTelefono=f'+56 9 {random.randint(1000, 9999)} {random.randint(1000, 9999)}',
                requiereReceta=1 if random.choice([True, False]) else 0,
                recetaRetirada=1 if random.choice([True, False]) else 0,
                metodoPago=random.choice(['EFECTIVO', 'TARJETA']),
                monto=random.uniform(5000, 50000),
                observaciones=f'Movimiento {i+1} para {farmacia.comuna}',
                requiereAutorizacion=1 if random.choice([True, False, False]) else 0,  # 33% de probabilidad
                fechaAutorizacion=fecha_creacion + timedelta(minutes=5) if random.choice([True, False]) else None,
                autorizadoPor=operador if random.choice([True, False]) else None,
                idFarmaciaDestino=None,
                idFarmaciaOrigen=farmacia,
                movimientoOrigen=None,
                rutMotorista=motorista,
                creado_por=operador,
                cantidad=random.randint(1, 3),
                intentos_entrega=1 if estado == 'ENTREGADO' else random.randint(0, 2),
                prioridad=random.choice([1, 2, 3]),
                producto=random.choice(productos),
                orden_despacho=None
            )
            
            # Crear movimiento específico según el tipo
            if movimiento.tipoMovimiento == 'DIRECTO':
                MovimientoDirecto.objects.create(
                    movimiento=movimiento,
                    direccionEntrega=movimiento.direccionDestino,
                    comunaEntrega=farmacia.comuna,
                    telefonoCliente=movimiento.clienteTelefono,
                    producto=movimiento.producto,
                    instrucciones=f'Entregar en recepción' if random.choice([True, False]) else None
                )
            elif movimiento.tipoMovimiento == 'RECETA':
                MovimientoReceta.objects.create(
                    movimiento=movimiento,
                    direccionEntrega=movimiento.direccionDestino,
                    comunaEntrega=farmacia.comuna,
                    telefonoCliente=movimiento.clienteTelefono,
                    producto=movimiento.producto,
                    archivoReceta=f'receta_{movimiento.idMovimiento}.pdf' if random.choice([True, False]) else None,
                    requiereRetiroReceta=movimiento.requiereReceta,
                    recetaRetirada=movimiento.recetaRetirada,
                    observaciones=movimiento.observaciones
                )
            
            movimientos_totales.append(movimiento)
            print(f"  Movimiento {movimiento.idMovimiento} creado - Motorista: {motorista.nombre} - Estado: {estado}")
    
    return movimientos_totales

def crear_reportes_basicos():
    """Crear configuraciones de reportes básicos"""
    print("\nCreando configuraciones de reportes...")
    
    # Obtener usuario administrador
    try:
        admin_user = User.objects.get(username='admin.logico')
    except User.DoesNotExist:
        admin_user = User.objects.filter(is_superuser=True).first()
    
    reportes = [
        {
            'nombre': 'Reporte Diario de Movimientos',
            'tipo_reporte': 'DIARIO',
            'formato_salida': 'PDF',
            'activo': True,
        },
        {
            'nombre': 'Reporte Semanal de Entregas',
            'tipo_reporte': 'SEMANAL',
            'formato_salida': 'EXCEL',
            'activo': True,
        },
        {
            'nombre': 'Reporte Mensual de Motoristas',
            'tipo_reporte': 'MENSUAL',
            'formato_salida': 'PDF',
            'activo': True,
        },
    ]
    
    for reporte_data in reportes:
        ConfiguracionReporte.objects.get_or_create(
            nombre=reporte_data['nombre'],
            defaults={
                'tipo_reporte': reporte_data['tipo_reporte'],
                'formato_salida': reporte_data['formato_salida'],
                'activo': reporte_data['activo'],
                'fecha_creacion': timezone.now()
            }
        )
    
    print("Configuraciones de reportes creadas ✓")

def verificar_creacion():
    """Verificar que todo se creó correctamente mostrando un resumen"""
    print("\n" + "="*60)
    print("RESUMEN DE DATOS CARGADOS")
    print("="*60)
    
    total_farmacias = Farmacia.objects.count()
    total_motos = Moto.objects.count()
    total_motoristas = Motorista.objects.count()
    total_asignaciones_motos = AsignacionMoto.objects.filter(activo=True).count()
    total_asignaciones_farmacias = AsignacionFarmacia.objects.filter(activo=True).count()
    total_movimientos = Movimiento.objects.count()
    
    print(f"Farmacias creadas: {total_farmacias}")
    print(f"Motos creadas: {total_motos}")
    print(f"Motoristas creados: {total_motoristas}")
    print(f"Asignaciones de motos activas: {total_asignaciones_motos}")
    print(f"Asignaciones a farmacias activas: {total_asignaciones_farmacias}")
    print(f"Movimientos creados: {total_movimientos}")
    
    # Mostrar motoristas sin asignaciones
    motoristas_sin_moto = Motorista.objects.filter(
        moto='SI',
        asignacionmoto__isnull=True
    ).count()
    motoristas_sin_farmacia = Motorista.objects.filter(
        asignacionfarmacia__isnull=True
    ).count()
    
    print(f"\nMotoristas sin moto asignada: {motoristas_sin_moto}")
    print(f"Motoristas sin farmacia asignada: {motoristas_sin_farmacia}")
    
    # Mostrar distribución de movimientos por estado
    from django.db import models
    estados = Movimiento.objects.values('estado').annotate(total=models.Count('idmovimiento'))
    print(f"\nDistribución de movimientos por estado:")
    for estado in estados:
        print(f"  {estado['estado']}: {estado['total']}")
    
    print("\n" + "="*60)
    print("DATOS DE PRUEBA CARGADOS EXITOSAMENTE")
    print("="*60)

def main():
    """Función principal que ejecuta todo el proceso"""
    print("INICIANDO CARGA DE DATOS DE PRUEBA PARA LOGICO")
    print("="*60)
    
    try:
        # 1. Crear configuraciones básicas
        crear_configuraciones_basicas()
        
        # 2. Crear farmacias
        farmacias = crear_farmacias()
        
        # 3. Crear motos
        motos = crear_motos()
        
        # 4. Crear motoristas
        motoristas = crear_motoristas()
        
        # 5. Crear asignaciones de motos
        asignaciones_motos = crear_asignaciones_motos(motos, motoristas)
        
        # 6. Crear asignaciones a farmacias (solo para motoristas con moto)
        asignaciones_farmacias = crear_asignaciones_farmacias(farmacias, motoristas, asignaciones_motos)
        
        # 7. Crear movimientos (solo para motoristas asignados a farmacias)
        movimientos = crear_movimientos(farmacias, asignaciones_farmacias)
        
        # 8. Crear reportes básicos
        #crear_reportes_basicos()
        
        # 9. Verificar creación
        #verificar_creacion()
        
        print("\nDATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print("\nREGLAS APLICADAS:")
        print("1. Solo motoristas con moto asignada pueden ser asignados a farmacias")
        print("2. Solo motoristas asignados a farmacias pueden generar movimientos")
        print("3. 2 motos quedaron sin asignar para pruebas")
        print("4. 2 motoristas no tienen moto asignada")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.movimiento.models import OrdenDespacho, Movimiento
from apps.farmacia.models import Farmacia
from apps.motorista.models import Motorista

# Obtener el modelo de Usuario personalizado
User = get_user_model()

class OrdenDespachoTestCase(TestCase):
    """
    Suite de pruebas para el modelo, vistas y lógica de negocio de OrdenDespacho.
    """

    def setUp(self):
        """
        Configuración inicial para las pruebas. Se ejecuta antes de cada test.
        Crea usuarios con diferentes roles, una farmacia, un motorista y datos básicos.
        """
        # Crear usuarios con roles
        self.gerente = User.objects.create_user(
            username='testgerente', password='password', rol='gerente', is_staff=True
        )
        self.supervisor = User.objects.create_user(
            username='testsupervisor', password='password', rol='supervisor'
        )
        self.operador = User.objects.create_user(
            username='testoperador', password='password', rol='operador'
        )
        self.motorista_user = User.objects.create_user(
            username='testmotorista', password='password', rol='motorista'
        )

        # Asignar permisos (simulado, en un proyecto real se usarían grupos y permisos)
        # Para simplificar, las vistas se prueban con el login de cada rol.
        # La lógica de permisos de Django se asume que funciona.

        # Crear datos relacionados
        self.farmacia = Farmacia.objects.create(nombre='Farmacia Central', comuna='Santiago')
        self.motorista = Motorista.objects.create(
            rut='11222333-4', nombre='Juan', apellidoPaterno='Perez', usuario=self.motorista_user
        )

        # Crear una Orden de Despacho para pruebas
        self.orden = OrdenDespacho.objects.create(
            cliente_nombre='Cliente de Prueba',
            cliente_telefono='987654321',
            direccion_entrega='Av. Siempre Viva 123',
            comuna_entrega='Springfield',
            metodo_pago='efectivo',
            monto_total=15000
        )

        self.client = Client()

    # --- Pruebas del Modelo OrdenDespacho ---

    def test_creacion_orden_y_numero_automatico(self):
        """Prueba que el número de orden se genera automáticamente en el formato correcto."""
        self.assertIsNotNone(self.orden.numero_orden)
        self.assertTrue(self.orden.numero_orden.startswith('OD-'))
        self.assertEqual(self.orden.estado, 'pendiente')
        self.assertEqual(str(self.orden), f"Orden #{self.orden.numero_orden} - {self.orden.cliente_nombre}")

    def test_actualizar_estado_orden_sin_movimientos(self):
        """El estado de la orden debe ser 'pendiente' si no tiene movimientos."""
        self.orden.actualizar_estado()
        self.assertEqual(self.orden.estado, 'pendiente')

    def test_actualizar_estado_orden_a_completado(self):
        """El estado debe ser 'completado' si todos sus movimientos están 'entregado'."""
        Movimiento.objects.create(
            orden_despacho=self.orden, tipoMovimiento='directo', estado='entregado',
            idFarmaciaOrigen=self.farmacia, rutMotorista=self.motorista
        )
        Movimiento.objects.create(
            orden_despacho=self.orden, tipoMovimiento='directo', estado='entregado',
            idFarmaciaOrigen=self.farmacia, rutMotorista=self.motorista
        )
        # La actualización se dispara desde el save() del movimiento, pero la llamamos explícitamente para asegurar.
        self.orden.actualizar_estado()
        self.assertEqual(self.orden.estado, 'completado')

    def test_actualizar_estado_orden_a_parcialmente_entregado(self):
        """El estado debe ser 'parcialmente_entregado' si algunos movimientos están entregados."""
        Movimiento.objects.create(
            orden_despacho=self.orden, tipoMovimiento='directo', estado='entregado',
            idFarmaciaOrigen=self.farmacia, rutMotorista=self.motorista
        )
        Movimiento.objects.create(
            orden_despacho=self.orden, tipoMovimiento='directo', estado='en_camino',
            idFarmaciaOrigen=self.farmacia, rutMotorista=self.motorista
        )
        self.orden.actualizar_estado()
        self.assertEqual(self.orden.estado, 'parcialmente_entregado')

    def test_actualizar_estado_orden_a_en_proceso(self):
        """El estado debe ser 'en_proceso' si hay movimientos pendientes o en camino."""
        Movimiento.objects.create(
            orden_despacho=self.orden, tipoMovimiento='directo', estado='pendiente',
            idFarmaciaOrigen=self.farmacia, rutMotorista=self.motorista
        )
        self.orden.actualizar_estado()
        self.assertEqual(self.orden.estado, 'en_proceso')

    def test_actualizar_estado_orden_a_fallido(self):
        """El estado debe ser 'fallido' si todos los movimientos están fallidos o anulados."""
        Movimiento.objects.create(
            orden_despacho=self.orden, tipoMovimiento='directo', estado='fallido',
            idFarmaciaOrigen=self.farmacia, rutMotorista=self.motorista
        )
        Movimiento.objects.create(
            orden_despacho=self.orden, tipoMovimiento='directo', estado='anulado',
            idFarmaciaOrigen=self.farmacia, rutMotorista=self.motorista
        )
        self.orden.actualizar_estado()
        self.assertEqual(self.orden.estado, 'fallido')

    def test_propiedades_calculadas_orden(self):
        """Prueba las propiedades 'movimientos_totales', 'movimientos_entregados' y 'porcentaje_completado'."""
        self.assertEqual(self.orden.movimientos_totales, 0)
        self.assertEqual(self.orden.movimientos_entregados, 0)
        self.assertEqual(self.orden.porcentaje_completado, 0)

        # Añadir movimientos
        Movimiento.objects.create(
            orden_despacho=self.orden, tipoMovimiento='directo', estado='entregado',
            idFarmaciaOrigen=self.farmacia, rutMotorista=self.motorista
        )
        Movimiento.objects.create(
            orden_despacho=self.orden, tipoMovimiento='directo', estado='entregado',
            idFarmaciaOrigen=self.farmacia, rutMotorista=self.motorista
        )
        Movimiento.objects.create(
            orden_despacho=self.orden, tipoMovimiento='directo', estado='pendiente',
            idFarmaciaOrigen=self.farmacia, rutMotorista=self.motorista
        )
        Movimiento.objects.create(
            orden_despacho=self.orden, tipoMovimiento='directo', estado='en_camino',
            idFarmaciaOrigen=self.farmacia, rutMotorista=self.motorista
        )

        # Refrescar la instancia de la orden para obtener los datos actualizados
        self.orden.refresh_from_db()

        self.assertEqual(self.orden.movimientos_totales, 4)
        self.assertEqual(self.orden.movimientos_entregados, 2)
        self.assertEqual(self.orden.porcentaje_completado, 50.0)

    # --- Pruebas de Vistas de OrdenDespacho ---

    def test_acceso_lista_ordenes_sin_login(self):
        """Prueba que un usuario no autenticado es redirigido desde la lista de órdenes."""
        response = self.client.get(reverse('movimiento:orden_list'))
        self.assertEqual(response.status_code, 302) # Redirección a login
        self.assertIn('/accounts/login/', response.url)

    def test_acceso_y_contenido_lista_ordenes_con_login(self):
        """Prueba que un usuario con permisos puede ver la lista de órdenes."""
        self.client.login(username='testsupervisor', password='password')
        response = self.client.get(reverse('movimiento:orden_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movimiento/ordendespacho_list.html')
        self.assertContains(response, 'Listado de Órdenes de Despacho')
        self.assertIn('ordenes', response.context)
        # Verificar que la orden creada en setUp aparece en la lista
        self.assertContains(response, self.orden.numero_orden)

    def test_filtro_busqueda_lista_ordenes(self):
        """Prueba la funcionalidad de búsqueda en la lista de órdenes."""
        self.client.login(username='testsupervisor', password='password')
        
        # Crear una segunda orden para asegurar que el filtro funciona
        orden_filtrada = OrdenDespacho.objects.create(
            cliente_nombre='Filtrado Test', cliente_telefono='111222333', direccion_entrega='Otra Calle',
            comuna_entrega='Otra Comuna', metodo_pago='tarjeta', monto_total=5000
        )

        # Buscar por nombre de cliente
        response = self.client.get(reverse('movimiento:orden_list'), {'q': 'Filtrado Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, orden_filtrada.numero_orden)
        self.assertNotContains(response, self.orden.numero_orden)

        # Buscar por número de orden
        response = self.client.get(reverse('movimiento:orden_list'), {'q': self.orden.numero_orden})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.orden.numero_orden)
        self.assertNotContains(response, orden_filtrada.numero_orden)

    def test_filtro_estado_lista_ordenes(self):
        """Prueba el filtro por estado en la lista de órdenes."""
        self.client.login(username='testsupervisor', password='password')
        
        orden_completada = OrdenDespacho.objects.create(
            cliente_nombre='Completado Test', estado='completado', cliente_telefono='111',
            direccion_entrega='...', comuna_entrega='...', metodo_pago='online', monto_total=10
        )

        # Filtrar por estado 'completado'
        response = self.client.get(reverse('movimiento:orden_list'), {'estado': 'completado'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, orden_completada.numero_orden)
        self.assertNotContains(response, self.orden.numero_orden) # La orden de setUp es 'pendiente'

    def test_vista_detalle_orden(self):
        """Prueba que la vista de detalle de orden muestra la información correcta."""
        self.client.login(username='testoperador', password='password')
        url = reverse('movimiento:orden_detalle', kwargs={'pk': self.orden.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movimiento/ordendespacho_detail.html')
        self.assertContains(response, self.orden.numero_orden)
        self.assertContains(response, self.orden.cliente_nombre)
        self.assertIn('orden', response.context)
        self.assertIn('movimientos_totales', response.context)
        self.assertIn('porcentaje_completado', response.context)

    def test_vista_detalle_orden_no_existente(self):
        """Prueba que la vista de detalle devuelve 404 para una orden que no existe."""
        self.client.login(username='testoperador', password='password')
        # UUID inválido
        import uuid
        url = reverse('movimiento:orden_detalle', kwargs={'pk': uuid.uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # --- Pruebas de Creación de OrdenDespacho ---

    def test_acceso_crear_orden_sin_permisos(self):
        """Prueba que un usuario sin permisos no puede acceder a la vista de creación."""
        self.client.login(username='testmotorista', password='password')
        response = self.client.get(reverse('movimiento:orden_crear'))
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_vista_crear_orden_get(self):
        """Prueba que la vista de creación se renderiza correctamente con una petición GET."""
        self.client.login(username='testoperador', password='password')
        response = self.client.get(reverse('movimiento:orden_crear'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movimiento/ordendespacho_form.html')
        self.assertIn('form', response.context)

    def test_crear_orden_post_valido(self):
        """Prueba la creación de una orden con datos válidos a través de una petición POST."""
        self.client.login(username='testoperador', password='password')
        
        orden_data = {
            'cliente_nombre': 'Nuevo Cliente',
            'cliente_telefono': '123456789',
            'direccion_entrega': 'Calle Falsa 456',
            'comuna_entrega': 'Shelbyville',
            'metodo_pago': 'tarjeta',
            'monto_total': 25000.00,
            'observaciones': 'Dejar en conserjería.'
        }

        response = self.client.post(reverse('movimiento:orden_crear'), data=orden_data)
        
        # Debería redirigir a la página de detalle de la nueva orden
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la orden fue creada en la base de datos
        nueva_orden = OrdenDespacho.objects.get(cliente_nombre='Nuevo Cliente')
        self.assertIsNotNone(nueva_orden)
        self.assertEqual(nueva_orden.monto_total, 25000.00)
        self.assertIn(str(nueva_orden.pk), response.url)

    def test_crear_orden_post_invalido(self):
        """Prueba que el formulario de creación muestra errores si los datos son inválidos."""
        self.client.login(username='testoperador', password='password')
        
        # Datos inválidos (falta cliente_nombre y monto_total)
        orden_data_invalida = {
            'cliente_telefono': '123456789',
            'direccion_entrega': 'Calle Falsa 456',
            'comuna_entrega': 'Shelbyville',
            'metodo_pago': 'tarjeta',
        }

        response = self.client.post(reverse('movimiento:orden_crear'), data=orden_data_invalida)
        
        self.assertEqual(response.status_code, 200) # No redirige, muestra el form con errores
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
        self.assertIn('cliente_nombre', response.context['form'].errors)
        self.assertIn('monto_total', response.context['form'].errors)

    # --- Pruebas del Dashboard de Órdenes ---

    def test_dashboard_ordenes_acceso_y_contexto(self):
        """Prueba el acceso y el contexto del dashboard de órdenes."""
        self.client.login(username='testsupervisor', password='password')
        response = self.client.get(reverse('movimiento:orden_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movimiento/dashboard_ordenes.html')
        
        # Verificar que las variables de contexto esperadas estén presentes
        self.assertIn('total_ordenes', response.context)
        self.assertIn('ordenes_por_estado', response.context)
        self.assertIn('ultimas_ordenes', response.context)
        
        # Verificar el valor inicial
        self.assertEqual(response.context['total_ordenes'], OrdenDespacho.objects.filter(activo=True).count())

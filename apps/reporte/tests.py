from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from datetime import date

# Importar los modelos necesarios para crear datos de prueba
from apps.farmacia.models import Farmacia
from apps.usuario.models import Usuario
from .models import ReporteGenerado

User = get_user_model()

class ReporteFarmaciaViewTest(TestCase):

    def setUp(self):
        """
        Configuración inicial para cada test.
        Se ejecuta antes de cada método de prueba.
        """
        # 1. Crear cliente de prueba
        self.client = Client()

        # 2. Crear grupos y permisos necesarios para el decorador @require_roles
        # Esto simula lo que hace tu script `crear_usuarios_roles.py`
        self.gerente_group, _ = Group.objects.get_or_create(name='Gerentes')

        # 3. Crear un usuario con el rol de gerente
        self.user = User.objects.create_user(
            username='testgerente',
            password='password123',
            rol='gerente'
        )
        self.user.groups.add(self.gerente_group)

        # 4. Crear datos de prueba para el modelo Farmacia
        Farmacia.objects.create(nombre='Farmacia Activa Santiago', comuna='Santiago', activo=True)
        Farmacia.objects.create(nombre='Farmacia Inactiva Santiago', comuna='Santiago', activo=False)
        Farmacia.objects.create(nombre='Farmacia Activa Providencia', comuna='Providencia', activo=True)

        # 5. Definir la URL para la vista de reporte de farmacia
        self.reporte_url = reverse('reporte:reporte_farmacia')

    def test_acceso_sin_autenticacion_redirige_al_login(self):
        """
        Verifica que un usuario no autenticado sea redirigido a la página de login.
        """
        response = self.client.get(self.reporte_url)
        self.assertEqual(response.status_code, 302) # 302 es el código para redirección
        self.assertIn('/accounts/login/', response.headers['Location'])

    def test_vista_reporte_farmacia_get_request(self):
        """
        Verifica que un usuario autenticado pueda acceder a la página del formulario (GET).
        """
        # Iniciar sesión con el usuario de prueba
        self.client.login(username='testgerente', password='password123')
        
        response = self.client.get(self.reporte_url)
        
        self.assertEqual(response.status_code, 200) # 200 = OK
        self.assertTemplateUsed(response, 'reporte/form_reporte.html')
        self.assertIn('form', response.context)
        self.assertIn('Reportes de Farmacias', response.content.decode('utf-8'))

    def test_generar_reporte_excel_post_request(self):
        """
        Prueba la generación de un reporte de farmacias en formato Excel (POST).
        """
        self.client.login(username='testgerente', password='password123')

        # Datos que se enviarían desde el formulario
        post_data = {
            'tipo_reporte': 'estado',
            'rango_fechas': 'personalizado',
            'fecha_desde': '2024-01-01',
            'fecha_hasta': date.today().strftime('%Y-%m-%d'),
            'estado_farmacia': 'activas',
            'comuna': 'Santiago',
            'formato_salida': 'xlsx'
        }

        response = self.client.post(self.reporte_url, data=post_data)

        self.assertEqual(response.status_code, 200)
        # Verificar que la respuesta es un archivo Excel
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename="reporte_farmacia_'))
        self.assertTrue(response['Content-Disposition'].endswith('.xlsx"'))

        # Verificar que se creó el registro en el historial de reportes
        self.assertTrue(ReporteGenerado.objects.filter(usuario=self.user, tipo_reporte='farmacia').exists())

    def test_generar_reporte_pdf_post_request(self):
        """
        Prueba la generación de un reporte de farmacias en formato PDF (POST).
        """
        self.client.login(username='testgerente', password='password123')

        post_data = {
            'tipo_reporte': 'comuna',
            'rango_fechas': 'todos',
            'formato_salida': 'pdf'
        }

        response = self.client.post(self.reporte_url, data=post_data)

        self.assertEqual(response.status_code, 200)
        # Verificar que la respuesta es un archivo PDF
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].endswith('.pdf"'))

        # Verificar que se creó el registro en el historial
        self.assertEqual(ReporteGenerado.objects.count(), 1)
        reporte = ReporteGenerado.objects.first()
        self.assertEqual(reporte.usuario, self.user) 
        self.assertEqual(reporte.formato, 'pdf') 

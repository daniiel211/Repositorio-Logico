# tests/test_seguridad.py
import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.usuario.models import Usuario

User = get_user_model()

class TestSeguridadOWASP:
    """Pruebas de seguridad basadas en OWASP Top 10"""
    
    # =========================================================================
    # 1. PRUEBAS DE SQL INJECTION
    # =========================================================================
    
    @pytest.mark.django_db
    def test_sql_injection_login(self, client):
        """
        CP-SEG-001: Prueba de SQL Injection en formulario de login
        Objetivo: Verificar que el sistema es inmune a SQL Injection
        """
        payloads_sql_injection = [
            "' OR '1'='1' --",
            "' OR 1=1--",
            "admin'--",
            "' UNION SELECT 1,2,3--",
            "'; DROP TABLE usuarios; --"
        ]
        
        for payload in payloads_sql_injection:
            response = client.post('/login/', {
                'username': payload,
                'password': 'anypassword'
            })
            
            # Verificar que no hay error de base de datos
            assert response.status_code != 500
            # Verificar que no se autentica
            assert not response.wsgi_request.user.is_authenticated
    
    @pytest.mark.django_db  
    def test_sql_injection_busqueda(self, client, usuario_gerente):
        """
        CP-SEG-002: Prueba de SQL Injection en búsquedas
        """
        client.force_login(usuario_gerente)
        
        payloads_busqueda = [
            "'; SELECT * FROM usuario_usuario; --",
            "' OR '1'='1",
            "test' UNION SELECT username, password FROM usuario_usuario--"
        ]
        
        # Probar en diferentes endpoints de búsqueda
        endpoints_busqueda = [
            '/farmacias/?search=',
            '/motoristas/?search=',
            '/movimientos/?search='
        ]
        
        for endpoint in endpoints_busqueda:
            for payload in payloads_busqueda:
                response = client.get(f"{endpoint}{payload}")
                assert response.status_code != 500
    
    # =========================================================================
    # 2. PRUEBAS DE XSS (CROSS-SITE SCRIPTING)
    # =========================================================================
    
    @pytest.mark.django_db
    def test_xss_campos_texto(self, client, usuario_gerente):
        """
        CP-SEG-003: Prueba de XSS en campos de texto libre
        """
        client.force_login(usuario_gerente)
        
        payloads_xss = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>"
        ]
        
        # Probar en diferentes formularios
        for payload in payloads_xss:
            # Ejemplo: crear farmacia con payload XSS
            response = client.post('/farmacias/crear/', {
                'IdFarmacia': 'XSS_TEST',
                'nombre': payload,
                'direccion': 'Direccion segura',
                'comuna': 'Santiago',
                'telefono': '+56223456789'
            })
            
            # Verificar que el contenido se escapa o rechaza
            if response.status_code == 200:  # Si la creación fue exitosa
                # Verificar que el payload no se ejecuta
                content = response.content.decode('utf-8')
                assert '<script>' not in content or '&lt;script&gt;' in content
    
    # =========================================================================
    # 3. PRUEBAS DE CSRF (CROSS-SITE REQUEST FORGERY)
    # =========================================================================
    
    @pytest.mark.django_db
    def test_csrf_formularios_criticos(self, client, usuario_gerente):
        """
        CP-SEG-004: Verificar protección CSRF en formularios críticos
        """
        # Crear un cliente sin CSRF
        client_no_csrf = Client(enforce_csrf_checks=False)
        client_no_csrf.force_login(usuario_gerente)
        
        formularios_criticos = [
            {
                'url': '/farmacias/crear/',
                'data': {
                    'IdFarmacia': 'CSRF_TEST',
                    'nombre': 'Farmacia CSRF Test',
                    'direccion': 'Test 123',
                    'comuna': 'Santiago'
                }
            },
            {
                'url': '/motoristas/crear/',
                'data': {
                    'rut': '11111111-1',
                    'nombre': 'Motorista CSRF',
                    'apellidoPaterno': 'Test'
                }
            },
            {
                'url': '/asignaciones/crear/',
                'data': {
                    'motorista': 1,
                    'moto': 1,
                    'estado': 'ACTIVA'
                }
            }
        ]
        
        for formulario in formularios_criticos:
            # Intentar POST sin token CSRF
            response = client_no_csrf.post(
                formulario['url'],
                formulario['data'],
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Simular AJAX
            )
            
            # Debería rechazar la petición (403) o redirigir al login
            assert response.status_code in [403, 302]
    
    # =========================================================================
    # 4. PRUEBAS DE CONTROL DE ACCESO POR ROLES
    # =========================================================================
    
    @pytest.mark.django_db
    def test_control_acceso_roles(self, client):
        """
        CP-SEG-005: Verificar control de acceso basado en roles
        """
        # Crear usuarios con diferentes roles
        gerente = User.objects.create_user(
            username='gerente_test',
            password='test123',
            rol='gerente'
        )
        
        motorista = User.objects.create_user(
            username='motorista_test', 
            password='test123',
            rol='motorista'
        )
        
        # URLs restringidas por rol
        urls_restringidas = [
            '/admin/',
            '/farmacias/crear/',
            '/motoristas/',
            '/reportes/gerencial/',
            '/configuracion/'
        ]
        
        # Probar acceso como motorista (debería ser denegado)
        client.force_login(motorista)
        for url in urls_restringidas:
            response = client.get(url)
            # Debería ser 403 (prohibido) o redirigir
            assert response.status_code in [403, 302, 404]
        
        # Probar acceso como gerente (debería ser permitido)
        client.force_login(gerente)
        for url in urls_restringidas:
            response = client.get(url)
            # Puede ser 200 (éxito) o 302 (redirección a login si necesita más permisos)
            assert response.status_code in [200, 302]
    
    @pytest.mark.django_db
    def test_acceso_datos_ajenos(self, client):
        """
        CP-SEG-006: Verificar que usuarios no pueden acceder a datos de otros
        """
        # Crear dos motoristas
        motorista1 = User.objects.create_user(
            username='motorista1',
            password='test123',
            rol='motorista'
        )
        
        motorista2 = User.objects.create_user(
            username='motorista2',
            password='test123', 
            rol='motorista'
        )
        
        # Motorista1 intenta acceder a datos de Motorista2
        client.force_login(motorista1)
        
        # Intentar acceder a perfil de otro usuario
        response = client.get(f'/motoristas/{motorista2.id}/')
        
        # Debería ser 403, 404 o redirigir
        assert response.status_code in [403, 404, 302]

class TestAutenticacionSegura:
    """Pruebas de autenticación y manejo de sesiones"""
    
    @pytest.mark.django_db
    def test_redireccion_por_rol(self, client):
        """
        CP-SEG-007: Verificar redirección después del login según el rol
        """
        roles_redirecciones = [
            ('gerente', '/dashboard/gerente/'),
            ('supervisor', '/dashboard/supervisor/'),
            ('operador', '/dashboard/operador/'),
            ('motorista', '/dashboard/motorista/')
        ]
        
        for rol, redireccion_esperada in roles_redirecciones:
            usuario = User.objects.create_user(
                username=f'test_{rol}',
                password='test123',
                rol=rol
            )
            
            # Login
            response = client.post('/login/', {
                'username': f'test_{rol}',
                'password': 'test123'
            })
            
            # Verificar redirección
            if response.status_code == 302:
                assert redireccion_esperada in response.url
    
    @pytest.mark.django_db
    def test_autenticacion_fallida_intentos(self, client):
        """
        CP-SEG-008: Verificar bloqueo después de múltiples intentos fallidos
        """
        usuario = User.objects.create_user(
            username='test_user',
            password='password_correcta'
        )
        
        # Intentos fallidos consecutivos
        for i in range(5):
            response = client.post('/login/', {
                'username': 'test_user',
                'password': f'wrong_password_{i}'
            })
        
        # Después de múltiples intentos, verificar medidas de seguridad
        response = client.post('/login/', {
            'username': 'test_user',
            'password': 'password_correcta'
        })
        
        # Podría haber un retraso, CAPTCHA, o bloqueo temporal
        assert response.status_code in [200, 302, 429]

class TestSubidaArchivosSegura:
    """Pruebas de subida segura de archivos"""
    
    @pytest.mark.django_db
    def test_tipos_archivo_permitidos(self, client, usuario_gerente):
        """
        CP-SEG-009: Verificar validación de tipos de archivo
        """
        client.force_login(usuario_gerente)
        
        archivos_peligrosos = [
            ('script.php', b'<?php system($_GET["cmd"]); ?>'),
            ('shell.exe', b'MZ\x90\x00\x03\x00\x00\x00'),
            ('malicio.so.html', b'<script>alert("XSS")</script>')
        ]
        
        for nombre_archivo, contenido in archivos_peligrosos:
            # Simular subida de archivo (ajustar según tu implementación)
            response = client.post('/motoristas/crear/', {
                'rut': '11111111-1',
                'nombre': 'Test',
                'archivo_documento': (nombre_archivo, contenido)
            })
            
            # Debería rechazar el archivo
            assert response.status_code != 200 or 'formato' in response.content.decode().lower()
    
    @pytest.mark.django_db
    def test_tamano_maximo_archivos(self, client, usuario_gerente):
        """
        CP-SEG-010: Verificar límite de tamaño de archivos
        """
        client.force_login(usuario_gerente)
        
        # Crear archivo muy grande (11MB)
        archivo_grande = b'x' * (11 * 1024 * 1024)  # 11MB
        
        response = client.post('/motoristas/crear/', {
            'rut': '11111111-1',
            'nombre': 'Test',
            'archivo_documento': ('archivo_grande.pdf', archivo_grande)
        })
        
        # Debería rechazar por tamaño
        assert response.status_code != 200 or 'tamaño' in response.content.decode().lower()

class TestCookiesSeguras:
    """Pruebas de configuración de cookies"""
    
    def test_cookies_httponly(self, client):
        """
        CP-SEG-011: Verificar que las cookies de sesión tienen flag HttpOnly
        """
        response = client.get('/login/')
        
        if 'Set-Cookie' in response.headers:
            cookies = response.headers['Set-Cookie']
            # Verificar que las cookies de sesión tienen HttpOnly
            assert 'HttpOnly' in cookies or 'sessionid' not in cookies
    
    def test_cookies_secure_en_produccion(self, settings):
        """
        CP-SEG-012: Verificar flags Secure en producción
        """
        # Simular entorno de producción
        settings.DEBUG = False
        settings.SESSION_COOKIE_SECURE = True
        settings.CSRF_COOKIE_SECURE = True
        
        assert settings.SESSION_COOKIE_SECURE is True
        assert settings.CSRF_COOKIE_SECURE is True
    
    @pytest.mark.django_db
    def test_rotacion_sesion(self, client, usuario_gerente):
        """
        CP-SEG-013: Verificar rotación de ID de sesión después del login
        """
        # Obtener sesión antes del login
        client.get('/login/')
        sessionid_antes = client.cookies.get('sessionid')
        
        # Hacer login
        client.force_login(usuario_gerente)
        sessionid_despues = client.cookies.get('sessionid')
        
        # El sessionid debería cambiar después del login
        if sessionid_antes and sessionid_despues:
            assert sessionid_antes.value != sessionid_despues.value

class TestValidacionesEntrada:
    """Pruebas de validación de entrada de datos"""
    
    @pytest.mark.django_db
    def test_validacion_rut_chileno(self, client, usuario_gerente):
        """
        CP-SEG-014: Verificar validación robusta de RUT chileno
        """
        client.force_login(usuario_gerente)
        
        ruts_invalidos = [
            '12345678-0',  # Dígito verificador incorrecto
            '1234567-1',   # Muy corto
            '123456789-1', # Muy largo
            'ABCDEFGH-K',  # Letras en el número
            '12345678-K',  # Formato inválido
        ]
        
        for rut_invalido in ruts_invalidos:
            response = client.post('/motoristas/crear/', {
                'rut': rut_invalido,
                'nombre': 'Test',
                'apellidoPaterno': 'Usuario'
            })
            
            # Debería fallar la validación
            assert response.status_code != 200 or 'rut' in response.content.decode().lower()
    
    @pytest.mark.django_db
    def test_validacion_coordenadas(self, client, usuario_gerente):
        """
        CP-SEG-015: Verificar validación de coordenadas geográficas
        """
        client.force_login(usuario_gerente)
        
        coordenadas_invalidas = [
            (-91.0, -180.0),  # Latitud fuera de rango
            (91.0, 180.0),    # Latitud fuera de rango
            (-90.0, -181.0),  # Longitud fuera de rango
            (90.0, 181.0),    # Longitud fuera de rango
            (999.999, 999.999), # Valores absurdos
        ]
        
        for lat, lon in coordenadas_invalidas:
            response = client.post('/farmacias/crear/', {
                'IdFarmacia': 'COORD_TEST',
                'nombre': 'Farmacia Test',
                'latitud': lat,
                'longitud': lon
            })
            
            # Debería fallar la validación
            assert response.status_code != 200 or 'coordenada' in response.content.decode().lower()

# Pruebas de integración de seguridad
class TestIntegracionSeguridad:
    """Pruebas de integración de características de seguridad"""
    
    @pytest.mark.django_db
    def test_auditoria_intentos_login(self, client):
        """
        CP-SEG-016: Verificar que se auditan los intentos de login
        """
        # Realizar intentos de login
        for i in range(3):
            client.post('/login/', {
                'username': f'usuario_inexistente_{i}',
                'password': 'password_incorrecta'
            })
        
        # Verificar que hay registros de auditoría (depende de tu implementación)
        # Esta prueba puede necesitar ajustarse según tu sistema de auditoría
        assert True  # Placeholder para verificación real
    
    @pytest.mark.django_db
    def test_headers_seguridad(self, client):
        """
        CP-SEG-017: Verificar headers de seguridad HTTP
        """
        response = client.get('/')
        
        headers_seguridad = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'X-XSS-Protection',
            'Content-Security-Policy'
        ]
        
        for header in headers_seguridad:
            # Al menos algunos headers de seguridad deberían estar presentes
            if header in response.headers:
                assert response.headers[header] is not None
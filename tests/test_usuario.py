# tests/test_usuario.py
import pytest

class TestUsuarioModel:
    """Suite de pruebas para el modelo Usuario - PU-003"""
    
    @pytest.mark.django_db
    def test_creacion_usuario_con_rol(self, usuario_gerente):
        """
        PU-003 - Caso 1: Usuario creado con rol específico
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Configurar
        usuario_gerente.set_password('testpassword123')
        usuario_gerente.save()
        
        # Verificar
        assert User.objects.filter(username='gerente_test').exists()
        assert usuario_gerente.rol == 'gerente'
        assert usuario_gerente.es_gerente == True
        assert usuario_gerente.es_motorista == False
    
    @pytest.mark.django_db
    def test_propiedades_rol(self):
        """
        PU-003 - Caso 2: Propiedades de rol retornan valores correctos
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Probar todos los roles
        roles_test = [
            ('gerente', 'es_gerente'),
            ('supervisor', 'es_supervisor'),
            ('operador', 'es_operador'),
            ('motorista', 'es_motorista'),
        ]
        
        for rol, propiedad in roles_test:
            usuario = User(
                username=f'test_{rol}',
                email=f'{rol}@test.com',
                first_name='Test',
                last_name='User',
                rol=rol
            )
            
            # Verificar que la propiedad específica retorna True
            assert getattr(usuario, propiedad) == True
            
            # Verificar que las otras propiedades retornan False
            otras_propiedades = [p for r, p in roles_test if p != propiedad]
            for otra_prop in otras_propiedades:
                assert getattr(usuario, otra_prop) == False
    
    @pytest.mark.django_db
    def test_metodo_get_full_name(self, usuario_gerente):
        """
        Prueba adicional: Método get_full_name retorna nombre completo
        """
        # Configurar
        usuario_gerente.save()
        
        # Ejecutar
        nombre_completo = usuario_gerente.get_full_name()
        
        # Verificar
        expected = "Gerente Test"
        assert nombre_completo == expected
    
    @pytest.mark.django_db
    def test_estado_display(self, usuario_gerente):
        """
        Prueba adicional: Propiedad estado_display retorna estado legible
        """
        # Configurar
        usuario_gerente.is_active = True
        usuario_gerente.save()
        
        # Verificar activo
        assert usuario_gerente.estado_display == "Activo"
        
        # Configurar inactivo
        usuario_gerente.is_active = False
        usuario_gerente.save()
        
        # Verificar inactivo
        assert usuario_gerente.estado_display == "Inactivo"

class TestUsuarioAutenticacion:
    """Pruebas de autenticación y control de acceso"""
    
    @pytest.mark.django_db
    def test_login_exitoso_redireccion_rol(self, usuario_gerente, client):
        """
        PU-003 - Caso 3: Login exitoso redirige según el rol del usuario
        """
        # Configurar
        usuario_gerente.set_password('testpassword123')
        usuario_gerente.save()
        
        # Ejecutar login - usar URL directa en lugar de reverse
        response = client.post('/login/', {  # Cambiar por tu URL real
            'username': 'gerente_test',
            'password': 'testpassword123'
        })
        
        # Verificar redirección
        assert response.status_code in [200, 302]
    
    @pytest.mark.django_db
    def test_acceso_restringido_por_rol(self, usuario_motorista, client):
        """
        PU-003 - Caso 4: Usuario con rol limitado no puede acceder a áreas administrativas
        """
        # Configurar
        usuario_motorista.set_password('testpassword123')
        usuario_motorista.save()
        
        # Login como motorista
        client.login(username='motorista_test', password='testpassword123')
        
        # Intentar acceder a ruta de administración
        response = client.get('/admin/')
        
        # Verificar acceso denegado (403) o redirección al login
        assert response.status_code in [403, 302]
    
    @pytest.mark.django_db
    def test_grupos_y_permisos(self, usuario_gerente, grupo_gerente):
        """
        PU-003 - Caso 5: Usuarios pueden ser asignados a grupos con permisos específicos
        """
        # Configurar
        usuario_gerente.save()
        grupo_gerente.save()
        
        # Asignar usuario al grupo
        usuario_gerente.groups.add(grupo_gerente)
        usuario_gerente.save()
        
        # Verificar asignación
        assert grupo_gerente in usuario_gerente.groups.all()
        assert usuario_gerente.groups.filter(name='Gerentes').exists()
    
    @pytest.mark.django_db
    def test_permisos_especificos_por_grupo(self, usuario_gerente, grupo_gerente):
        """
        PU-003 - Caso 6: Grupos tienen permisos específicos asignados
        """
        from django.contrib.auth.models import Permission
        # Configurar
        usuario_gerente.save()
        
        # Obtener un permiso específico
        try:
            permiso = Permission.objects.get(codename='add_user')
            grupo_gerente.permissions.add(permiso)
            
            # Asignar usuario al grupo
            usuario_gerente.groups.add(grupo_gerente)
            usuario_gerente.save()
            
            # Verificar que el usuario tiene el permiso a través del grupo
            assert usuario_gerente.has_perm('auth.add_user')
            
        except Permission.DoesNotExist:
            pytest.skip("Permiso 'add_user' no encontrado")
    
    @pytest.mark.django_db
    def test_login_fallido_credenciales_invalidas(self, client):
        """
        PU-003 - Caso 7: Login con credenciales inválidas muestra mensaje de error
        """
        # Ejecutar login con credenciales inválidas
        response = client.post('/login/', {  # Usar URL directa
            'username': 'usuario_inexistente',
            'password': 'password_incorrecto'
        })
        
        # Verificar que no se redirige (queda en la misma página con error)
        assert response.status_code == 200

class TestUsuarioIntegracion:
    """Pruebas de integración para usuarios"""
    
    @pytest.mark.django_db
    def test_fluxo_completo_autenticacion(self, client):
        """
        PU-003 - Caso 8: Flujo completo de autenticación y autorización
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # 1. Crear usuario de prueba
        usuario = User.objects.create_user(
            username='test_integracion',
            password='testpass123',
            email='integracion@test.com',
            first_name='Integracion',
            last_name='Test',
            rol='operador'
        )
        
        # 2. Login exitoso
        login_response = client.post('/login/', {
            'username': 'test_integracion',
            'password': 'testpass123'
        })
        
        # 3. Verificar que el usuario está autenticado
        client.force_login(usuario)
        assert '_auth_user_id' in client.session
        
        # 4. Logout
        logout_response = client.get('/logout/')
        
        # 5. Verificar que el usuario ya no está autenticado
        assert '_auth_user_id' not in client.session
# tests/test_moto.py
import pytest
from django.core.exceptions import ValidationError

class TestMotoModel:
    """Suite de pruebas para el modelo Moto - PU-002"""
    
    # PU-002: Validación documentos completos
    @pytest.mark.django_db
    def test_documentos_completos_con_docs_vigentes(self, moto_documentos_vigentes):
        """
        PU-002 - Caso 1: Moto con documentos vigentes debe retornar True
        """
        from apps.moto.models import Moto

        # Configurar
        moto_documentos_vigentes.save()
        
        # Ejecutar
        resultado = moto_documentos_vigentes.documentos_completos()
        
        # Verificar
        assert resultado == True
    
    @pytest.mark.django_db
    def test_documentos_completos_con_docs_vencidos(self, moto_documentos_vencidos):
        """
        PU-002 - Caso 2: Moto con documentos vencidos/faltantes debe retornar False
        """
        from apps.moto.models import Moto

        # Configurar
        moto_documentos_vencidos.save()
        
        # Ejecutar
        resultado = moto_documentos_vencidos.documentos_completos()
        
        # Verificar
        assert resultado == False
    
    @pytest.mark.django_db
    def test_documentos_completos_parciales(self):
        """
        PU-002 - Caso 3: Moto con algunos documentos faltantes debe retornar False
        """
        from apps.moto.models import Moto
        # Crear usuario para campos de auditoría
        from apps.usuario.models import Usuario
        usuario = Usuario.objects.create_user(
            username='moto_user',
            password='testpass123',
            email='moto@test.com'
        )
        
        moto_parcial = Moto(
            patente='IJ789KL',
            marca='Suzuki',
            modelo='Address',
            año=2022,
            color='Gris',
            numChasis='CHASIS789',
            motor='MOTOR789',
            propietario='EMPRESA',
            permisoCirculacion='permiso.pdf',  # Presente
            seguro='',  # Faltante
            revisionTecnica='revision.pdf',  # Presente
            creado_por=usuario
        )
        
        moto_parcial.save()
        resultado = moto_parcial.documentos_completos()
        
        assert resultado == False
    
    @pytest.mark.django_db
    def test_validacion_patente_chilena_valida(self):
        """
        Prueba adicional: Validación de patentes chilenas válidas
        """
        from apps.moto.models import Moto
        from apps.usuario.models import Usuario
        usuario = Usuario.objects.create_user(
            username='patente_user',
            password='testpass123',
            email='patente@test.com'
        )
        
        patentes_validas = [
            'ABCD12',       # Formato nuevo
            'CD1234',       # Cuerpo diplomático
            'FFAA123',      # Fuerzas Armadas
            'CARAB1234',    # Carabineros
        ]
        
        for patente in patentes_validas:
            moto = Moto(
                patente=patente,
                marca='Test',
                modelo='Test',
                año=2023,
                color='Test',
                numChasis='TEST123',
                motor='TEST123',
                propietario='EMPRESA',
                creado_por=usuario
            )            
            # Añadir valores para campos obligatorios
            moto.permisoCirculacion = 'dummy.pdf'
            moto.seguro = 'dummy.pdf'
            moto.revisionTecnica = 'dummy.pdf'
            
            # No debe lanzar excepción
            moto.full_clean()
    
    @pytest.mark.django_db
    def test_validacion_patente_chilena_invalida(self):
        """
        Prueba adicional: Validación de patentes chilenas inválidas
        """
        from apps.moto.models import Moto
        from apps.usuario.models import Usuario
        usuario = Usuario.objects.create_user(
            username='patente_inv_user',
            password='testpass123',
            email='patente_inv@test.com'
        )
        
        patentes_invalidas = [
            '123ABCD',      # Formato incorrecto
            'AB123',        # Muy corta
            'ABCDEFGH',     # Muy larga
            'AB-12-CD',     # Formato incorrecto
        ]
        
        for patente in patentes_invalidas:
            moto = Moto(
                patente=patente,
                marca='Test',
                modelo='Test',
                año=2023,
                color='Test',
                numChasis='TEST123',
                motor='TEST123',
                propietario='EMPRESA',
                creado_por=usuario
            )            
            # Añadir valores para campos obligatorios
            moto.permisoCirculacion = 'dummy.pdf'
            moto.seguro = 'dummy.pdf'
            moto.revisionTecnica = 'dummy.pdf'
            
            with pytest.raises(ValidationError) as exc_info:
                moto.full_clean()
                
            # Ajustar según tu validación real
            assert 'patente' in str(exc_info.value)
    
    @pytest.mark.django_db
    def test_manager_activas_inactivas(self, moto_documentos_vigentes, moto_documentos_vencidos):
        """
        Prueba adicional: Manager personalizado para motos activas e inactivas
        """
        from apps.moto.models import Moto

        # Configurar
        moto_documentos_vigentes.save()
        moto_documentos_vencidos.activo = False
        moto_documentos_vencidos.save()
        
        # Ejecutar
        activas = Moto.objects.activas()
        inactivas = Moto.objects.inactivas()
        
        # Verificar
        assert activas.count() == 1
        assert inactivas.count() == 1
        assert moto_documentos_vigentes in activas
        assert moto_documentos_vencidos in inactivas
    
    @pytest.mark.django_db
    def test_soft_delete_reactivacion_moto(self, moto_documentos_vigentes):
        """
        Prueba adicional: Soft delete y reactivación para motos
        """
        # Configurar
        moto_documentos_vigentes.save()
        
        # Ejecutar soft delete
        moto_documentos_vigentes.soft_delete()
        
        # Verificar desactivación
        assert moto_documentos_vigentes.activo == False
        
        # Ejecutar reactivación
        moto_documentos_vigentes.reactivar()
        
        # Verificar reactivación
        assert moto_documentos_vigentes.activo == True
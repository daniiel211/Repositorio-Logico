# tests/test_models.py
import pytest
from apps.farmacia.models import Farmacia
from apps.asignacion.models import AsignacionMoto, AsignacionFarmacia
from apps.movimiento.models import Movimiento

class TestFarmaciaModel:
    """Pruebas para el modelo Farmacia"""
    
    @pytest.mark.django_db
    def test_creacion_farmacia_valida(self):
        """Prueba creación de farmacia con datos válidos"""
        farmacia = Farmacia(
            IdFarmacia='TEST001',
            nombre='Farmacia Test',
            direccion='Av. Test 123',
            comuna='Santiago',
            provincia='Santiago',
            region='Metropolitana',
            apertura='08:00:00',
            cierre='22:00:00',
            telefono='+56223456789',
            latitud=-33.456789,
            longitud=-70.648000
        )
        
        farmacia.full_clean()
        farmacia.save()
        
        assert Farmacia.objects.filter(IdFarmacia='TEST001').exists()
    
    @pytest.mark.django_db  
    def test_soft_delete_farmacia(self):
        """Prueba soft delete de farmacia"""
        farmacia = Farmacia.objects.create(
            IdFarmacia='TEST002',
            nombre='Farmacia Delete',
            direccion='Test 456',
            comuna='Santiago',
            provincia='Santiago',
            region='Metropolitana',
            apertura='08:00:00',
            cierre='22:00:00',
            telefono='+56223456789'
        )
        
        farmacia.soft_delete()
        assert farmacia.activo == False
        
        farmacia.reactivar()
        assert farmacia.activo == True

class TestAsignacionModels:
    """Pruebas para modelos de asignación"""
    
    @pytest.mark.django_db
    def test_creacion_asignacion_moto(self, motorista_valido, moto_documentos_vigentes):
        """Prueba creación de asignación moto-motorista"""
        # Configurar
        motorista_valido.save()
        moto_documentos_vigentes.save()
        
        # Crear asignación
        asignacion = AsignacionMoto.objects.create(
            motorista=motorista_valido,
            moto=moto_documentos_vigentes,
            estado=AsignacionMoto.ESTADO_ACTIVA,
            observaciones='Asignación de prueba',
            creado_por_id=1  # Asumiendo que existe un usuario con id 1
        )
        
        # Verificar
        assert AsignacionMoto.objects.filter(motorista=motorista_valido).exists()
        assert asignacion.estado == 'ACTIVA'
        assert asignacion.duracion_asignacion is not None

@pytest.mark.django_db
class TestMovimientoModel:
    """Pruebas para el modelo Movimiento"""
    
    def test_creacion_movimiento_directo(self, motorista_valido):
        """Prueba creación de movimiento directo"""
        from apps.farmacia.models import Farmacia
        
        # Configurar
        motorista_valido.save()
        farmacia = Farmacia.objects.create(
            IdFarmacia='MOVTEST',
            nombre='Farmacia Movimiento',
            direccion='Test 789',
            comuna='Santiago',
            provincia='Santiago',
            region='Metropolitana',
            apertura='08:00:00',
            cierre='22:00:00',
            telefono='+56223456789'
        )
        
        # Crear movimiento
        movimiento = Movimiento.objects.create(
            idFarmaciaOrigen=farmacia,
            rutMotorista=motorista_valido,
            tipoMovimiento='directo',
            estado='pendiente',
            direccionDestino='Av. Entrega 123',
            clienteNombre='Cliente Test',
            clienteTelefono='+56912345678',
            requiereReceta=False,
            metodoPago='efectivo',
            monto=15000.00,
            observaciones='Movimiento de prueba'
        )
        
        # Verificar
        assert Movimiento.objects.filter(idMovimiento=movimiento.idMovimiento).exists()
        assert movimiento.estado == 'pendiente'
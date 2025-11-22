# tests/conftest.py
import pytest
import os
import django
from django.conf import settings

# Configurar Django ANTES de cualquier importación
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LogiCo_.settings')

if not settings.configured:
    django.setup()

from apps.motorista.models import Motorista
from apps.moto.models import Moto
from apps.usuario.models import Usuario
from django.contrib.auth.models import Group, Permission

@pytest.fixture
def motorista_valido():
    """Fixture para crear un motorista válido"""
    return Motorista(
        rut='12345678-9',
        nombre='Juan',
        apellidoPaterno='Pérez',
        apellidoMaterno='González',
        fechaNacimiento='1990-05-15',
        direccion='Av. Test 123',
        comuna='Santiago',
        provincia='Santiago',
        region='Metropolitana',
        telefono='+56912345678',
        correo='test@test.com',
        moto='NO',
        archivo='licencia.pdf',
        fechaUltControl='2024-01-15',
        fechaControl='2024-07-15',
        fechaVencimiento='2025-01-15',
        parentesco='PADRE',
        telefonoEmergencia='+56987654321',
        nombreContacto='Carlos',
        apellidoContacto='Pérez',
        direccionContacto='Av. Test 123'
    )

@pytest.fixture
def moto_documentos_vigentes():
    """Fixture para crear moto con documentos vigentes"""
    return Moto(
        patente='AB123CD',
        marca='Yamaha',
        modelo='NMAX',
        año=2023,
        color='Negro',
        numChasis='CHASIS123',
        motor='MOTOR123',
        propietario='EMPRESA',
        permisoCirculacion='permiso_vigente.pdf',
        seguro='seguro_vigente.pdf',
        revisionTecnica='revision_vigente.pdf'
    )

@pytest.fixture
def moto_documentos_vencidos():
    """Fixture para crear moto con documentos vencidos"""
    return Moto(
        patente='EF456GH',
        marca='Honda',
        modelo='PCX',
        año=2020,
        color='Blanco',
        numChasis='CHASIS456',
        motor='MOTOR456',
        propietario='EMPRESA',
        permisoCirculacion='',  # Documento faltante
        seguro='seguro_vencido.pdf',
        revisionTecnica=''  # Documento faltante
    )

@pytest.fixture
def usuario_gerente():
    """Fixture para crear usuario con rol gerente"""
    return Usuario(
        username='gerente_test',
        email='gerente@test.com',
        first_name='Gerente',
        last_name='Test',
        rol='gerente'
    )

@pytest.fixture
def usuario_motorista():
    """Fixture para crear usuario con rol motorista"""
    return Usuario(
        username='motorista_test',
        email='motorista@test.com',
        first_name='Motorista',
        last_name='Test',
        rol='motorista'
    )

@pytest.fixture
def grupo_gerente():
    """Fixture para crear grupo de gerentes"""
    group, created = Group.objects.get_or_create(name='Gerentes')
    return group

@pytest.fixture
def grupo_motorista():
    """Fixture para crear grupo de motoristas"""
    group, created = Group.objects.get_or_create(name='Motoristas')
    return group
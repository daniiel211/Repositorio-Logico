from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    """Modelo principal de usuarios del sistema Logico"""

    ROL_CHOICES = [
        ('gerente', 'Gerente General'),
        ('supervisor', 'Supervisor'),
        ('operador', 'Operador'),
        ('motorista', 'Motorista'),
    ]

    # Campos personalizados adicionales
    rut = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        verbose_name='RUT'
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Teléfono'
    )
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='operador',
        verbose_name='Rol del usuario'
    )
    fecha_registro = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de registro'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )

    # Configuran campos existentes de AbstractUser
    first_name = models.CharField(
        max_length=150,
        verbose_name='Nombre'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Apellido'
    )
    email = models.EmailField(
        verbose_name='Correo electrónico'
    )

    class Meta:
        db_table = 'USUARIO'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def es_gerente(self):
        return self.rol == 'gerente'

    @property
    def es_supervisor(self):
        return self.rol == 'supervisor'

    @property
    def es_operador(self):
        return self.rol == 'operador'

    @property
    def es_motorista(self):
        return self.rol == 'motorista'

    @property
    def estado_display(self):
        return "Activo" if self.is_active else "Inactivo"
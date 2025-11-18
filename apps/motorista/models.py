"""
Modelo Motorista para la aplicación de motoristas
Define la estructura de datos para los motoristas del sistema
"""

from django.db import models
from django.conf import settings  # Importar settings para usar AUTH_USER_MODEL
from django.core.exceptions import ValidationError

def validar_rut_chileno(value):
    """
    Valida que el RUT chileno tenga formato correcto y dígito verificador válido
    Implementa el algoritmo oficial de validación de RUT chileno
    """
    # Limpiar y estandarizar el formato
    rut = value.upper().replace(".", "").replace("-", "")
    
    # Validar longitud mínima
    if len(rut) < 2:
        raise ValidationError("RUT demasiado corto")
    
    # Separar cuerpo y dígito verificador
    cuerpo = rut[:-1]
    dv = rut[-1]
    
    # Validar que el cuerpo sea numérico
    if not cuerpo.isdigit():
        raise ValidationError("La parte numérica del RUT debe contener solo dígitos")
    
    # Calcular dígito verificador esperado
    suma = 0
    multiplo = 2
    
    # Algoritmo de cálculo de dígito verificador
    for reverso in reversed(cuerpo):
        suma += int(reverso) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2
    
    # Calcular dígito verificador
    resto = suma % 11
    dv_calculado = 11 - resto
    
    # Ajustar casos especiales
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)

    # Validar coincidencia
    if dv_calculado != dv:
        raise ValidationError("El dígito verificador del RUT no es válido")
    
    return value

class Motorista(models.Model):
    """
    Modelo que representa un motorista en el sistema
    Contiene información personal, profesional y de contacto de emergencia
    """
    
    # Opciones para campos de selección
    OPCIONES_MOTO = [
        ('SI', 'Sí'),
        ('NO', 'No'),
    ]

    OPCIONES_PARENTESCO = [
        ('PADRE', 'Padre'),
        ('MADRE', 'Madre'),
        ('HERMANO', 'Hermano'),
        ('HERMANA', 'Hermana'),
        ('TIO', 'Tío'),
        ('TIA', 'Tía'),
        ('PRIMO', 'Primo'),
        ('PRIMA', 'Prima'),
        ('AMIGO', 'Amigo'),
        ('AMIGA', 'Amiga'),
        ('OTRO', 'Otro'),
    ]

    # Identificación única del motorista
    rut = models.CharField(
        primary_key=True,
        max_length=12,
        verbose_name="RUT",
        validators=[validar_rut_chileno]
    )
    
    # Información personal
    nombre = models.CharField(max_length=50, verbose_name="Nombres")
    apellidoPaterno = models.CharField(max_length=50, verbose_name="Apellido Paterno")
    apellidoMaterno = models.CharField(max_length=50, verbose_name="Apellido Materno")
    fechaNacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    
    # Dirección y ubicación
    direccion = models.CharField(max_length=200, verbose_name="Dirección")
    comuna = models.CharField(max_length=50, verbose_name="Comuna")
    provincia = models.CharField(max_length=50, verbose_name="Provincia")
    region = models.CharField(max_length=50, verbose_name="Región")
    
    # Información de contacto
    telefono = models.CharField(max_length=15, verbose_name="Teléfono")
    correo = models.EmailField(verbose_name="Correo Electrónico")
    
    # Información profesional
    moto = models.CharField(max_length=2, choices=OPCIONES_MOTO, verbose_name="¿Tiene Moto?")
    archivo = models.FileField(upload_to='licencias/', verbose_name="Licencia de Conductor")
    fechaUltControl = models.DateField(verbose_name="Fecha Último Control")
    fechaControl = models.DateField(verbose_name="Fecha Próximo Control")
    fechaVencimiento = models.DateField(verbose_name="Fecha Vencimiento Licencia")
    
    # Contacto de emergencia
    parentesco = models.CharField(max_length=50, choices=OPCIONES_PARENTESCO, verbose_name="Parentesco Contacto")
    telefonoEmergencia = models.CharField(max_length=15, verbose_name="Teléfono Emergencia")
    nombreContacto = models.CharField(max_length=100, default='N/A', verbose_name="Nombre Contacto")
    apellidoContacto = models.CharField(max_length=100, default='N/A', verbose_name="Apellido Contacto")
    direccionContacto = models.CharField(max_length=200, default='N/A', verbose_name="Dirección Contacto")
    
    # Campos de auditoría - CORREGIDO: usar settings.AUTH_USER_MODEL
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # CORREGIDO
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='motoristas_creados'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # CORREGIDO
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='motoristas_modificados'
    )
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Configuración meta del modelo Motorista
        """
        verbose_name = "Motorista"
        verbose_name_plural = "Motoristas"
        ordering = ['apellidoPaterno', 'nombre']
        db_table = 'motorista'

    def __str__(self):
        """
        Representación en string del motorista
        """
        return f"{self.nombre} {self.apellidoPaterno} - {self.rut}"

    def soft_delete(self):
        """
        Marca el motorista como inactivo (eliminación lógica)
        """
        self.activo = False
        self.save()

    def reactivar(self):
        """
        Reactiva un motorista previamente marcado como inactivo
        """
        self.activo = True
        self.save()

    def nombre_completo(self):
        """
        Retorna el nombre completo del motorista
        Incluye ambos apellidos
        """
        return f"{self.nombre} {self.apellidoPaterno} {self.apellidoMaterno}"
from django import forms
from django.utils import timezone
from datetime import datetime, timedelta

class FiltroBaseForm(forms.Form):
    """Formulario base para filtros de reportes"""
    
    RANGO_FECHA_CHOICES = [
        ('hoy', 'Hoy'),
        ('ayer', 'Ayer'),
        ('semana_actual', 'Semana Actual'),
        ('semana_pasada', 'Semana Pasada'),
        ('mes_actual', 'Mes Actual'),
        ('mes_pasado', 'Mes Pasado'),
        ('anio_actual', 'Año Actual'),
        ('personalizado', 'Personalizado'),
    ]
    
    rango_fecha = forms.ChoiceField(
        choices=RANGO_FECHA_CHOICES,
        initial='mes_actual',
        label='Rango de Fecha'
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha Desde'
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha Hasta'
    )
    
    formato_salida = forms.ChoiceField(
        choices=[('pdf', 'PDF'), ('excel', 'Excel')],
        initial='pdf',
        label='Formato de Salida'
    )

    def clean(self):
        cleaned_data = super().clean()
        rango_fecha = cleaned_data.get('rango_fecha')
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        
        if rango_fecha == 'personalizado':
            if not fecha_desde or not fecha_hasta:
                raise forms.ValidationError('Para rango personalizado, debe especificar fecha desde y hasta.')
            if fecha_desde > fecha_hasta:
                raise forms.ValidationError('La fecha desde no puede ser mayor que la fecha hasta.')
        
        return cleaned_data
    
    def get_fechas(self):
        """Retorna las fechas según el rango seleccionado"""
        rango_fecha = self.cleaned_data.get('rango_fecha')
        hoy = timezone.now().date()
        
        if rango_fecha == 'personalizado':
            return self.cleaned_data.get('fecha_desde'), self.cleaned_data.get('fecha_hasta')
        
        elif rango_fecha == 'hoy':
            return hoy, hoy
        
        elif rango_fecha == 'ayer':
            ayer = hoy - timedelta(days=1)
            return ayer, ayer
        
        elif rango_fecha == 'semana_actual':
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            return inicio_semana, hoy
        
        elif rango_fecha == 'semana_pasada':
            hoy = timezone.now().date()
            inicio_semana_pasada = hoy - timedelta(days=hoy.weekday() + 7)
            fin_semana_pasada = inicio_semana_pasada + timedelta(days=6)
            return inicio_semana_pasada, fin_semana_pasada
        
        elif rango_fecha == 'mes_actual':
            inicio_mes = hoy.replace(day=1)
            return inicio_mes, hoy
        
        elif rango_fecha == 'mes_pasado':
            primer_dia_mes_actual = hoy.replace(day=1)
            ultimo_dia_mes_pasado = primer_dia_mes_actual - timedelta(days=1)
            primer_dia_mes_pasado = ultimo_dia_mes_pasado.replace(day=1)
            return primer_dia_mes_pasado, ultimo_dia_mes_pasado
        
        elif rango_fecha == 'anio_actual':
            inicio_anio = hoy.replace(month=1, day=1)
            return inicio_anio, hoy
        
        return None, None

class ReporteFarmaciaForm(FiltroBaseForm):
    """Formulario para reportes de farmacias"""
    
    TIPO_REPORTE_CHOICES = [
        ('estado', 'Reporte por Estado'),
        ('comuna', 'Reporte por Comuna'),
        ('actividad', 'Reporte de Actividad'),
    ]
    
    tipo_reporte = forms.ChoiceField(
        choices=TIPO_REPORTE_CHOICES,
        initial='estado',
        label='Tipo de Reporte'
    )
    
    estado_farmacia = forms.ChoiceField(
        choices=[('', 'Todos'), ('activas', 'Activas'), ('inactivas', 'Inactivas')],
        required=False,
        label='Estado Farmacia'
    )
    
    comuna = forms.CharField(
        required=False,
        max_length=50,
        label='Comuna'
    )

class ReporteMotoristaForm(FiltroBaseForm):
    """Formulario para reportes de motoristas"""
    
    TIPO_REPORTE_CHOICES = [
        ('general', 'Reporte General'),
        ('licencias', 'Licencias por Vencer'),
        ('eficiencia', 'Eficiencia de Motoristas'),
    ]
    
    tipo_reporte = forms.ChoiceField(
        choices=TIPO_REPORTE_CHOICES,
        initial='general',
        label='Tipo de Reporte'
    )
    
    estado_motorista = forms.ChoiceField(
        choices=[('', 'Todos'), ('activos', 'Activos'), ('inactivos', 'Inactivos')],
        required=False,
        label='Estado Motorista'
    )
    
    dias_vencimiento = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=365,
        initial=30,
        label='Días para vencimiento de licencia'
    )

class ReporteMotoForm(FiltroBaseForm):
    """Formulario para reportes de motos"""
    
    TIPO_REPORTE_CHOICES = [
        ('general', 'Reporte General'),
        ('documentos', 'Estado de Documentos'),
        ('asignadas', 'Motos Asignadas/No Asignadas'),
    ]
    
    tipo_reporte = forms.ChoiceField(
        choices=TIPO_REPORTE_CHOICES,
        initial='general',
        label='Tipo de Reporte'
    )
    
    estado_moto = forms.ChoiceField(
        choices=[('', 'Todas'), ('activas', 'Activas'), ('inactivas', 'Inactivas')],
        required=False,
        label='Estado Moto'
    )
    
    propietario = forms.ChoiceField(
        choices=[('', 'Todos'), ('EMPRESA', 'Empresa'), ('MOTORISTA', 'Motorista')],
        required=False,
        label='Propietario'
    )

class ReporteAsignacionForm(FiltroBaseForm):
    """Formulario para reportes de asignaciones"""
    
    TIPO_REPORTE_CHOICES = [
        ('moto', 'Asignaciones de Motos'),
        ('farmacia', 'Asignaciones de Farmacias'),
        ('historial', 'Historial Completo'),
    ]
    
    tipo_reporte = forms.ChoiceField(
        choices=TIPO_REPORTE_CHOICES,
        initial='moto',
        label='Tipo de Reporte'
    )
    
    estado_asignacion = forms.ChoiceField(
        choices=[('', 'Todos'), ('ACTIVA', 'Activas'), ('FINALIZADA', 'Finalizadas')],
        required=False,
        label='Estado Asignación'
    )

class ReporteMovimientoForm(FiltroBaseForm):
    """Formulario para reportes de movimientos"""
    
    TIPO_REPORTE_CHOICES = [
        ('general', 'Reporte General'),
        ('por_tipo', 'Movimientos por Tipo'),
        ('por_estado', 'Movimientos por Estado'),
        ('eficiencia', 'Eficiencia de Entregas'),
    ]
    
    tipo_reporte = forms.ChoiceField(
        choices=TIPO_REPORTE_CHOICES,
        initial='general',
        label='Tipo de Reporte'
    )
    
    tipo_movimiento = forms.ChoiceField(
        choices=[
            ('', 'Todos'), 
            ('directo', 'Directo'), 
            ('receta', 'Receta'), 
            ('traslado', 'Traslado'), 
            ('reenvio', 'Reenvío')
        ],
        required=False,
        label='Tipo Movimiento'
    )
    
    estado_movimiento = forms.ChoiceField(
        choices=[
            ('', 'Todos'),
            ('pendiente', 'Pendiente'),
            ('en_camino', 'En Camino'),
            ('entregado', 'Entregado'),
            ('fallido', 'Fallido'),
        ],
        required=False,
        label='Estado Movimiento'
    )

class ReporteIncidenciasForm(FiltroBaseForm):
    """Formulario para reportes de incidencias"""
    
    TIPO_REPORTE_CHOICES = [
        ('general', 'Reporte General'),
        ('por_tipo', 'Incidencias por Tipo'),
        ('por_estado', 'Incidencias por Estado'),
        ('por_gravedad', 'Incidencias por Gravedad'),
        ('tiempos_resolucion', 'Tiempos de Resolución'),
    ]
    
    ESTADO_INCIDENCIA_CHOICES = [
        ('', 'Todos los estados'),
        ('REGISTRADA', 'Registrada'),
        ('EN_REVISION', 'En Revisión'),
        ('RESUELTA', 'Resuelta'),
        ('ESCALADA', 'Escalada'),
        ('CERRADA', 'Cerrada'),
    ]
    
    GRAVEDAD_CHOICES = [
        ('', 'Todas las gravedades'),
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica'),
    ]
    
    tipo_reporte = forms.ChoiceField(
        choices=TIPO_REPORTE_CHOICES,
        initial='general',
        label='Tipo de Reporte'
    )
    
    estado_incidencia = forms.ChoiceField(
        choices=ESTADO_INCIDENCIA_CHOICES,
        required=False,
        label='Estado de Incidencia'
    )
    
    tipo_incidencia = forms.ModelChoiceField(
        queryset=None,  # Se establecerá en __init__
        required=False,
        label='Tipo de Incidencia'
    )
    
    gravedad = forms.ChoiceField(
        choices=GRAVEDAD_CHOICES,
        required=False,
        label='Nivel de Gravedad'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Importar aquí para evitar importaciones circulares
        from apps.configuracion.models import TipoIncidencia
        self.fields['tipo_incidencia'].queryset = TipoIncidencia.objects.filter(activo=True)
    
    def clean(self):
        cleaned_data = super().clean()
        # Validaciones adicionales específicas para incidencias
        tipo_reporte = cleaned_data.get('tipo_reporte')
        
        if tipo_reporte == 'tiempos_resolucion':
            # Para reportes de tiempos de resolución, sugerir un rango de fechas mayor
            fecha_desde = cleaned_data.get('fecha_desde')
            fecha_hasta = cleaned_data.get('fecha_hasta')
            
            if fecha_desde and fecha_hasta:
                dias_rango = (fecha_hasta - fecha_desde).days
                if dias_rango < 7:
                    self.add_warning('Para reportes de tiempos de resolución se recomienda un rango mínimo de 7 días.')
        
        return cleaned_data
    
    def get_fechas(self):
        """Sobrescribir para ajustar fechas por defecto para incidencias"""
        rango_fecha = self.cleaned_data.get('rango_fecha')
        
        if rango_fecha == 'personalizado':
            return self.cleaned_data.get('fecha_desde'), self.cleaned_data.get('fecha_hasta')
        
        # Para incidencias, por defecto usar el último mes
        hoy = timezone.now().date()
        if not rango_fecha or rango_fecha == 'mes_actual':
            inicio_mes = hoy.replace(day=1)
            return inicio_mes, hoy
        
        # Usar la lógica base para otros rangos
        return super().get_fechas()
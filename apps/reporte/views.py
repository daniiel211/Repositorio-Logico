from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q, Sum, Avg, Case, When, FloatField, F, Min, Max
from django.utils import timezone
from datetime import datetime, timedelta
import json
import io
import xlsxwriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch

from .decorators import require_roles
from .forms import (
    ReporteFarmaciaForm, ReporteMotoristaForm, ReporteMotoForm,
    ReporteAsignacionForm, ReporteMovimientoForm, ReporteIncidenciasForm,
    ReporteOrdenesForm
)
from .models import ReporteGenerado

@login_required
@require_roles(['gerente', 'supervisor', 'operador'])
def dashboard_reportes(request):
    """Dashboard principal de reportes"""
    context = {
        'titulo': 'Sistema de Reportes - LogiCo',
        'modulos_disponibles': obtener_modulos_por_rol(request.user)
    }
    return render(request, 'reporte/dashboard.html', context)

@login_required
@require_roles(['gerente', 'supervisor', 'operador'])
def reporte_farmacia(request):
    """Vista para generar reportes de farmacias"""
    if request.method == 'POST':
        form = ReporteFarmaciaForm(request.POST)
        if form.is_valid():
            return generar_reporte_farmacia(request, form)
    else:
        form = ReporteFarmaciaForm()
    
    context = {
        'form': form,
        'titulo': 'Reportes de Farmacias',
        'modulo': 'farmacia'
    }
    return render(request, 'reporte/form_reporte.html', context)

@login_required
@require_roles(['gerente', 'supervisor', 'operador'])
def reporte_motorista(request):
    """Vista para generar reportes de motoristas"""
    if request.method == 'POST':
        form = ReporteMotoristaForm(request.POST)
        if form.is_valid():
            return generar_reporte_motorista(request, form)
    else:
        form = ReporteMotoristaForm()
    
    context = {
        'form': form,
        'titulo': 'Reportes de Motoristas',
        'modulo': 'motorista'
    }
    return render(request, 'reporte/form_reporte.html', context)

@login_required
@require_roles(['gerente', 'supervisor', 'operador'])
def reporte_moto(request):
    """Vista para generar reportes de motos"""
    if request.method == 'POST':
        form = ReporteMotoForm(request.POST)
        if form.is_valid():
            return generar_reporte_moto(request, form)
    else:
        form = ReporteMotoForm()
    
    context = {
        'form': form,
        'titulo': 'Reportes de Motos',
        'modulo': 'moto'
    }
    return render(request, 'reporte/form_reporte.html', context)

@login_required
@require_roles(['gerente', 'supervisor'])
def reporte_asignacion(request):
    """Vista para generar reportes de asignaciones"""
    if request.method == 'POST':
        form = ReporteAsignacionForm(request.POST)
        if form.is_valid():
            return generar_reporte_asignacion(request, form)
    else:
        form = ReporteAsignacionForm()
    
    context = {
        'form': form,
        'titulo': 'Reportes de Asignaciones',
        'modulo': 'asignacion'
    }
    return render(request, 'reporte/form_reporte.html', context)

@login_required
@require_roles(['gerente', 'supervisor', 'operador'])
def reporte_movimiento(request):
    """Vista para generar reportes de movimientos"""
    if request.method == 'POST':
        form = ReporteMovimientoForm(request.POST)
        if form.is_valid():
            return generar_reporte_movimiento(request, form)
    else:
        form = ReporteMovimientoForm()
    
    context = {
        'form': form,
        'titulo': 'Reportes de Movimientos',
        'modulo': 'movimiento'
    }
    return render(request, 'reporte/form_reporte.html', context)

@login_required
@require_roles(['gerente', 'supervisor'])
def reporte_ordenes(request):
    """Vista para generar reportes de órdenes de despacho"""
    if request.method == 'POST':
        form = ReporteOrdenesForm(request.POST)
        if form.is_valid():
            return generar_reporte_ordenes(request, form)
    else:
        form = ReporteOrdenesForm()
    
    context = {
        'form': form,
        'titulo': 'Reportes de Órdenes de Despacho',
        'modulo': 'ordenes'
    }
    return render(request, 'reporte/form_reporte.html', context)

@login_required
@require_roles(['gerente', 'supervisor'])
def reporte_incidencias(request):
    """Vista para generar reportes de incidencias"""
    if request.method == 'POST':
        form = ReporteIncidenciasForm(request.POST)
        if form.is_valid():
            return generar_reporte_incidencias(request, form)
    else:
        form = ReporteIncidenciasForm()
    
    context = {
        'form': form,
        'titulo': 'Reportes de Incidencias',
        'modulo': 'incidencias'
    }
    return render(request, 'reporte/form_reporte.html', context)

@login_required
@require_roles(['gerente'])
def reporte_gerencial(request):
    """Vista para generar reportes de gerenciales"""
    # This is a placeholder for your gerencial report logic.
    # For now, it will render a simple page.
    # You can create a specific form like ReporteGerencialForm if needed.
    
    context = {
        'form': None, # Replace with your form if you create one
        'titulo': 'Reportes Gerenciales',
        'modulo': 'gerencial'
    }
    return render(request, 'reporte/form_reporte.html', context)

@login_required
@require_roles(['gerente', 'supervisor', 'operador'])
def historial_reportes(request):
    """Muestra el historial de reportes generados por el usuario"""
    reportes = ReporteGenerado.objects.filter(usuario=request.user).order_by('-fecha_generacion')
    
    context = {
        'reportes': reportes,
        'titulo': 'Historial de Reportes Generados'
    }
    return render(request, 'reporte/historial.html', context)

# Funciones de generación de reportes
def generar_reporte_farmacia(request, form):
    """Genera reporte de farmacias en PDF o Excel"""
    from apps.farmacia.models import Farmacia
    
    fecha_desde, fecha_hasta = form.get_fechas()
    tipo_reporte = form.cleaned_data['tipo_reporte']
    formato = form.cleaned_data['formato_salida']
    
    # Construir queryset base
    farmacias = Farmacia.objects.all()
    
    # Aplicar filtros
    estado = form.cleaned_data.get('estado_farmacia')
    if estado == 'activas':
        farmacias = farmacias.filter(activo=True)
    elif estado == 'inactivas':
        farmacias = farmacias.filter(activo=False)
    
    comuna = form.cleaned_data.get('comuna')
    if comuna:
        farmacias = farmacias.filter(comuna__icontains=comuna)
    
    # Preparar datos según tipo de reporte
    if tipo_reporte == 'estado':
        datos = farmacias.values('comuna').annotate(
            total=Count('IdFarmacia'),
            activas=Count('IdFarmacia', filter=Q(activo=True)),
            inactivas=Count('IdFarmacia', filter=Q(activo=False))
        ).order_by('comuna')
        titulo = f"Reporte de Farmacias por Estado - {fecha_desde} a {fecha_hasta}"
        
    elif tipo_reporte == 'comuna':
        datos = farmacias.values('comuna', 'region').annotate(
            total=Count('IdFarmacia')
        ).order_by('region', 'comuna')
        titulo = f"Reporte de Farmacias por Comuna - {fecha_desde} a {fecha_hasta}"
        
    else:  # actividad
        datos = farmacias.values('nombre', 'comuna', 'activo', 'fecha_creacion')
        titulo = f"Reporte de Actividad de Farmacias - {fecha_desde} a {fecha_hasta}"
    
    return generar_documento_reporte(request, datos, titulo, 'farmacia', formato, form.cleaned_data)

def generar_reporte_motorista(request, form):
    """Genera reporte de motoristas en PDF o Excel"""
    from apps.motorista.models import Motorista
    
    fecha_desde, fecha_hasta = form.get_fechas()
    tipo_reporte = form.cleaned_data['tipo_reporte']
    formato = form.cleaned_data['formato_salida']
    
    motoristas = Motorista.objects.all()
    
    # Aplicar filtros
    estado = form.cleaned_data.get('estado_motorista')
    if estado == 'activos':
        motoristas = motoristas.filter(activo=True)
    elif estado == 'inactivos':
        motoristas = motoristas.filter(activo=False)
    
    if tipo_reporte == 'licencias':
        dias = form.cleaned_data.get('dias_vencimiento', 30)
        fecha_limite = timezone.now().date() + timedelta(days=dias)
        motoristas = motoristas.filter(
            fechaVencimiento__lte=fecha_limite,
            activo=True
        )
        titulo = f"Motoristas con Licencias por Vencer (próximos {dias} días)"
        
    elif tipo_reporte == 'eficiencia':
        # Aquí integrarías con datos de movimientos para calcular eficiencia
        motoristas = motoristas.filter(activo=True)
        titulo = f"Reporte de Eficiencia de Motoristas - {fecha_desde} a {fecha_hasta}"
        
    else:  # general
        titulo = f"Reporte General de Motoristas - {fecha_desde} a {fecha_hasta}"
    
    datos = motoristas.values(
        'rut', 'nombre', 'apellidoPaterno', 'apellidoMaterno', 
        'comuna', 'activo', 'fechaVencimiento'
    )
    
    return generar_documento_reporte(request, datos, titulo, 'motorista', formato, form.cleaned_data)

def generar_reporte_moto(request, form):
    """Genera reporte de motos en PDF o Excel"""
    from apps.moto.models import Moto
    
    fecha_desde, fecha_hasta = form.get_fechas()
    tipo_reporte = form.cleaned_data['tipo_reporte']
    formato = form.cleaned_data['formato_salida']
    
    motos = Moto.objects.all()
    
    # Aplicar filtros
    estado = form.cleaned_data.get('estado_moto')
    if estado == 'activas':
        motos = motos.filter(activo=True)
    elif estado == 'inactivas':
        motos = motos.filter(activo=False)
    
    propietario = form.cleaned_data.get('propietario')
    if propietario:
        motos = motos.filter(propietario=propietario)
    
    if tipo_reporte == 'documentos':
        motos = motos.filter(activo=True)
        titulo = f"Estado de Documentos de Motos - {fecha_desde} a {fecha_hasta}"
        
    elif tipo_reporte == 'asignadas':
        from apps.asignacion.models import AsignacionMoto
        motos_asignadas = AsignacionMoto.objects.filter(
            estado='ACTIVA', activo=True
        ).values_list('moto__patente', flat=True)
        
        motos = motos.filter(activo=True)
        titulo = f"Motos Asignadas vs No Asignadas - {fecha_desde} a {fecha_hasta}"
        
    else:  # general
        titulo = f"Reporte General de Motos - {fecha_desde} a {fecha_hasta}"
    
    datos = motos.values(
        'patente', 'marca', 'modelo', 'año', 'color', 'propietario', 'activo'
    )
    
    return generar_documento_reporte(request, datos, titulo, 'moto', formato, form.cleaned_data)

def generar_reporte_asignacion(request, form):
    """Genera reporte de asignaciones en PDF o Excel"""
    from apps.asignacion.models import AsignacionMoto, AsignacionFarmacia
    
    fecha_desde, fecha_hasta = form.get_fechas()
    tipo_reporte = form.cleaned_data['tipo_reporte']
    formato = form.cleaned_data['formato_salida']
    
    estado = form.cleaned_data.get('estado_asignacion')
    
    if tipo_reporte == 'moto':
        asignaciones = AsignacionMoto.objects.all()
        if estado:
            asignaciones = asignaciones.filter(estado=estado)
        titulo = f"Reporte de Asignaciones de Motos - {fecha_desde} a {fecha_hasta}"
        datos = asignaciones.values(
            'motorista__nombre', 'motorista__apellidoPaterno',
            'moto__patente', 'moto__marca', 'moto__modelo',
            'estado', 'fecha_asignacion', 'fecha_finalizacion'
        )
        
    elif tipo_reporte == 'farmacia':
        asignaciones = AsignacionFarmacia.objects.all()
        if estado:
            asignaciones = asignaciones.filter(estado=estado)
        titulo = f"Reporte de Asignaciones de Farmacias - {fecha_desde} a {fecha_hasta}"
        datos = asignaciones.values(
            'motorista__nombre', 'motorista__apellidoPaterno',
            'farmacia__nombre', 'farmacia__comuna',
            'estado', 'fecha_asignacion', 'fecha_finalizacion'
        )
        
    else:  # historial
        titulo = f"Historial Completo de Asignaciones - {fecha_desde} a {fecha_hasta}"
        # Combinar ambos tipos de asignaciones
        datos_motos = AsignacionMoto.objects.values(
            'motorista__nombre', 'motorista__apellidoPaterno',
            'moto__patente', 'estado', 'fecha_asignacion', 'fecha_finalizacion'
        )
        datos_farmacias = AsignacionFarmacia.objects.values(
            'motorista__nombre', 'motorista__apellidoPaterno',
            'farmacia__nombre', 'estado', 'fecha_asignacion', 'fecha_finalizacion'
        )
        datos = list(datos_motos) + list(datos_farmacias)
    
    return generar_documento_reporte(request, datos, titulo, 'asignacion', formato, form.cleaned_data)

def generar_reporte_movimiento(request, form):
    """Genera reporte de movimientos en PDF o Excel"""
    from apps.movimiento.models import Movimiento
    
    fecha_desde, fecha_hasta = form.get_fechas()
    tipo_reporte = form.cleaned_data['tipo_reporte']
    formato = form.cleaned_data['formato_salida']
    
    movimientos = Movimiento.objects.all()
    
    # Aplicar filtros de fecha si están disponibles en el modelo
    if hasattr(Movimiento, 'fechaCreacion'):
        if fecha_desde and fecha_hasta:
            movimientos = movimientos.filter(
                fechaCreacion__date__range=[fecha_desde, fecha_hasta]
            )
    
    tipo_movimiento = form.cleaned_data.get('tipo_movimiento')
    if tipo_movimiento:
        movimientos = movimientos.filter(tipoMovimiento=tipo_movimiento)
    
    estado_movimiento = form.cleaned_data.get('estado_movimiento')
    if estado_movimiento:
        movimientos = movimientos.filter(estado=estado_movimiento)
    
    if tipo_reporte == 'por_tipo':
        datos = movimientos.values('tipoMovimiento').annotate(
            total=Count('idMovimiento')
        ).order_by('-total')
        titulo = f"Movimientos por Tipo - {fecha_desde} a {fecha_hasta}"
        
    elif tipo_reporte == 'por_estado':
        datos = movimientos.values('estado').annotate(
            total=Count('idMovimiento')
        ).order_by('-total')
        titulo = f"Movimientos por Estado - {fecha_desde} a {fecha_hasta}"
        
    elif tipo_reporte == 'eficiencia':
        datos = movimientos.values('rutMotorista__nombre', 'rutMotorista__apellidoPaterno').annotate(
            total=Count('idMovimiento'),
            entregados=Count('idMovimiento', filter=Q(estado='entregado')),
            tasa_exito=Avg(Case(When(estado='entregado', then=1), default=0, output_field=FloatField()))
        ).order_by('-tasa_exito')
        titulo = f"Eficiencia de Entregas - {fecha_desde} a {fecha_hasta}"
        
    else:  # general
        datos = movimientos.values(
            'idMovimiento', 'tipoMovimiento', 'estado',
            'fechaCreacion', 'rutMotorista__nombre', 'idFarmaciaOrigen__nombre'
        )
        titulo = f"Reporte General de Movimientos - {fecha_desde} a {fecha_hasta}"
    
    return generar_documento_reporte(request, datos, titulo, 'movimiento', formato, form.cleaned_data)

def generar_reporte_incidencias(request, form):
    """Genera reporte de incidencias en PDF o Excel"""
    from apps.configuracion.models import IncidenciaMovimiento, TipoIncidencia
    
    fecha_desde, fecha_hasta = form.get_fechas()
    tipo_reporte = form.cleaned_data['tipo_reporte']
    formato = form.cleaned_data['formato_salida']
    
    incidencias = IncidenciaMovimiento.objects.all()
    
    # Aplicar filtros de fecha
    if fecha_desde and fecha_hasta:
        incidencias = incidencias.filter(
            fecha_incidencia__date__range=[fecha_desde, fecha_hasta]
        )
    
    # Aplicar filtros adicionales
    estado_incidencia = form.cleaned_data.get('estado_incidencia')
    if estado_incidencia:
        incidencias = incidencias.filter(estado=estado_incidencia)
    
    tipo_incidencia = form.cleaned_data.get('tipo_incidencia')
    if tipo_incidencia:
        incidencias = incidencias.filter(tipo_incidencia=tipo_incidencia)
    
    gravedad = form.cleaned_data.get('gravedad')
    if gravedad:
        incidencias = incidencias.filter(tipo_incidencia__gravedad=gravedad)
    
    if tipo_reporte == 'por_tipo':
        datos = incidencias.values('tipo_incidencia__nombre').annotate(
            total=Count('id'),
            resueltas=Count('id', filter=Q(estado='RESUELTA')),
            pendientes=Count('id', filter=Q(estado__in=['REGISTRADA', 'EN_REVISION']))
        ).order_by('-total')
        titulo = f"Incidencias por Tipo - {fecha_desde} a {fecha_hasta}"
        
    elif tipo_reporte == 'por_estado':
        datos = incidencias.values('estado').annotate(
            total=Count('id')
        ).order_by('-total')
        titulo = f"Incidencias por Estado - {fecha_desde} a {fecha_hasta}"
        
    elif tipo_reporte == 'por_gravedad':
        datos = incidencias.values('tipo_incidencia__gravedad').annotate(
            total=Count('id')
        ).order_by('-total')
        titulo = f"Incidencias por Gravedad - {fecha_desde} a {fecha_hasta}"
        
    elif tipo_reporte == 'tiempos_resolucion':
        # Solo incidencias resueltas
        incidencias_resueltas = incidencias.filter(estado='RESUELTA')
        datos = incidencias_resueltas.values(
            'tipo_incidencia__nombre', 'tipo_incidencia__gravedad'
        ).annotate(
            total=Count('id'),
            tiempo_promedio_horas=Avg(
                (F('fecha_resolucion') - F('fecha_incidencia')) / 3600.0
            )
        ).order_by('tipo_incidencia__gravedad', '-total')
        titulo = f"Tiempos de Resolución de Incidencias - {fecha_desde} a {fecha_hasta}"
        
    else:  # general
        datos = incidencias.values(
            'id', 'tipo_incidencia__nombre', 'estado',
            'fecha_incidencia', 'fecha_resolucion',
            'reportada_por__first_name', 'reportada_por__last_name',
            'movimiento__idMovimiento'
        )
        titulo = f"Reporte General de Incidencias - {fecha_desde} a {fecha_hasta}"
    
    return generar_documento_reporte(request, datos, titulo, 'incidencias', formato, form.cleaned_data)

def generar_reporte_ordenes(request, form):
    """Genera reporte de órdenes de despacho en PDF o Excel"""
    from apps.movimiento.models import OrdenDespacho
    
    fecha_desde, fecha_hasta = form.get_fechas()
    tipo_reporte = form.cleaned_data['tipo_reporte']
    formato = form.cleaned_data['formato_salida']
    
    ordenes = OrdenDespacho.objects.all()
    
    # Aplicar filtros de fecha
    if fecha_desde and fecha_hasta:
        ordenes = ordenes.filter(
            fecha_creacion__date__range=[fecha_desde, fecha_hasta]
        )
    
    # Aplicar filtros adicionales
    estado_orden = form.cleaned_data.get('estado_orden')
    if estado_orden:
        ordenes = ordenes.filter(estado=estado_orden)
    
    if tipo_reporte == 'por_estado':
        datos = ordenes.values('estado').annotate(
            total=Count('id')
        ).order_by('-total')
        titulo = f"Órdenes de Despacho por Estado - {fecha_desde} a {fecha_hasta}"
        
    elif tipo_reporte == 'por_farmacia':
        datos = ordenes.values('farmacia_origen__nombre').annotate(
            total=Count('id')
        ).order_by('-total')
        titulo = f"Órdenes de Despacho por Farmacia de Origen - {fecha_desde} a {fecha_hasta}"
        
    elif tipo_reporte == 'sin_movimiento':
        datos = ordenes.filter(movimientos__isnull=True).values(
            'numero_orden', 'cliente_nombre', 'estado', 'fecha_creacion'
        )
        titulo = f"Órdenes sin Movimientos Asociados - {fecha_desde} a {fecha_hasta}"
        
    else:  # general
        datos = ordenes.annotate(num_movimientos=Count('movimientos')).values(
            'numero_orden', 'cliente_nombre', 'estado',
            'fecha_creacion', 'farmacia_origen__nombre', 'num_movimientos'
        )
        titulo = f"Reporte General de Órdenes de Despacho - {fecha_desde} a {fecha_hasta}"
    
    return generar_documento_reporte(request, datos, titulo, 'ordenes', formato, form.cleaned_data)


def generar_documento_reporte(request, datos, titulo, modulo, formato, filtros):
    """Función central para generar documentos PDF o Excel"""
    
    # Registrar el reporte generado
    reporte = ReporteGenerado.objects.create(
        usuario=request.user,
        tipo_reporte=modulo,
        nombre_archivo=f"reporte_{modulo}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{formato}",
        formato=formato,
        estado='completado',
        filtros_aplicados=filtros
    )
    
    if formato == 'pdf':
        return generar_pdf(datos, titulo, modulo, filtros)
    else:
        return generar_excel(datos, titulo, modulo, filtros)

def generar_pdf(datos, titulo, modulo, filtros):
    """Genera un reporte en formato PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Centrado
    )
    
    # Título
    elements.append(Paragraph(titulo, title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Información de la empresa y filtros
    empresa_info = [
        f"<b>Empresa:</b> Discopro Ltda.",
        f"<b>Sistema:</b> LogiCo - Sistema de Gestión Logística",
        f"<b>Módulo:</b> {modulo.capitalize()}",
        f"<b>Fecha de generación:</b> {timezone.now().strftime('%Y-%m-%d %H:%M')}",
    ]
    
    # Información de filtros (solo si hay filtros aplicados)
    if filtros:
        filtros_texto = "<b>Filtros aplicados:</b><br/>"
        for key, value in filtros.items():
            if value:  # Solo mostrar filtros con valores
                filtros_texto += f"- {key}: {value}<br/>"
        empresa_info.append(filtros_texto)
    
    for info in empresa_info:
        elements.append(Paragraph(info, styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de datos
    if datos:
        # Preparar encabezados
        headers = list(datos[0].keys()) if datos else []
        
        # Mejorar nombres de encabezados
        headers_mejorados = []
        for header in headers:
            header_mejorado = header.replace('_', ' ').title()
            header_mejorado = header_mejorado.replace('Id', 'ID')
            header_mejorado = header_mejorado.replace('Farmacia', 'Farmacia')
            header_mejorado = header_mejorado.replace('Motorista', 'Motorista')
            headers_mejorados.append(header_mejorado)
        
        data = [headers_mejorados]
        
        # Preparar datos
        for item in datos:
            row = []
            for key in headers:
                value = item.get(key, '')
                # Formatear valores específicos
                if isinstance(value, datetime):
                    value = value.strftime('%d/%m/%Y %H:%M')
                elif isinstance(value, timedelta):
                    # Convertir timedelta a horas
                    total_horas = value.total_seconds() / 3600
                    value = f"{total_horas:.2f} horas"
                row.append(str(value))
            data.append(row)
        
        # Crear tabla
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("No hay datos disponibles para los filtros seleccionados.", styles['Normal']))
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{modulo}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    return response

def generar_excel(datos, titulo, modulo, filtros):
    """Genera un reporte en formato Excel"""
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet('Reporte')
    
    # Formatos
    title_format = workbook.add_format({
        'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter'
    })
    header_format = workbook.add_format({
        'bold': True, 'bg_color': '#366092', 'font_color': 'white', 
        'border': 1, 'align': 'center'
    })
    cell_format = workbook.add_format({'border': 1, 'align': 'center'})
    
    # Escribir información de la empresa
    worksheet.merge_range('A1:F1', 'Discopro Ltda.', title_format)
    worksheet.merge_range('A2:F2', 'LogiCo - Sistema de Gestión Logística', title_format)
    worksheet.merge_range('A3:F3', titulo, title_format)
    
    row = 5
    worksheet.write(row, 0, 'Módulo:')
    worksheet.write(row, 1, modulo.capitalize())
    row += 1
    worksheet.write(row, 0, 'Fecha generación:')
    worksheet.write(row, 1, timezone.now().strftime('%Y-%m-%d %H:%M'))
    row += 2
    
    # Escribir datos
    if datos:
        headers = list(datos[0].keys())
        
        # Mejorar nombres de encabezados
        headers_mejorados = []
        for header in headers:
            header_mejorado = header.replace('_', ' ').title()
            header_mejorado = header_mejorado.replace('Id', 'ID')
            header_mejorado = header_mejorado.replace('Farmacia', 'Farmacia')
            header_mejorado = header_mejorado.replace('Motorista', 'Motorista')
            headers_mejorados.append(header_mejorado)
        
        # Escribir encabezados
        for col, header in enumerate(headers_mejorados):
            worksheet.write(row, col, header, header_format)
        
        # Escribir datos
        for data_row in datos:
            row += 1
            for col, key in enumerate(headers):
                value = data_row.get(key, '')
                # Formatear valores específicos
                if isinstance(value, datetime):
                    value = value.strftime('%d/%m/%Y %H:%M')
                elif isinstance(value, timedelta):
                    # Convertir timedelta a horas
                    total_horas = value.total_seconds() / 3600
                    value = f"{total_horas:.2f} horas"
                worksheet.write(row, col, str(value), cell_format)
    
    # Ajustar ancho de columnas
    if datos:
        worksheet.set_column(0, len(headers) - 1, 15)
    
    workbook.close()
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="reporte_{modulo}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    return response

def obtener_modulos_por_rol(usuario):
    """Retorna los módulos de reporte disponibles según el rol del usuario"""
    modulos_base = ['farmacia', 'motorista', 'moto', 'movimiento', 'ordenes']
    
    if hasattr(usuario, 'rol') and usuario.rol == 'gerente':
        return modulos_base + ['asignacion', 'incidencias']
    elif hasattr(usuario, 'rol') and usuario.rol == 'supervisor':
        return modulos_base + ['asignacion', 'incidencias']
    elif hasattr(usuario, 'rol') and usuario.rol == 'operador':
        return modulos_base
    
    return []
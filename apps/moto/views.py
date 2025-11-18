from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Moto
from .forms import MotoForm, MotoSearchForm

@login_required
def dashboard_moto(request):
    """Dashboard principal del módulo moto"""
    total_motos = Moto.objects.count()
    motos_activas = Moto.objects.activas().count()
    motos_inactivas = Moto.objects.inactivas().count()
    motos_sin_documentos = Moto.objects.activas().filter(
        Q(permisoCirculacion='') | Q(seguro='') | Q(revisionTecnica='')
    ).count()

    context = {
        'total_motos': total_motos,
        'motos_activas': motos_activas,
        'motos_inactivas': motos_inactivas,
        'motos_sin_documentos': motos_sin_documentos,
    }
    return render(request, 'moto/dashboard.html', context)

@login_required
def listar_motos(request):
    """Lista todas las motos con opciones de búsqueda y filtro"""
    form = MotoSearchForm(request.GET or None)
    motos = Moto.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('q')
        estado = form.cleaned_data.get('estado')

        if query:
            motos = motos.filter(
                Q(patente__icontains=query) |
                Q(marca__icontains=query) |
                Q(modelo__icontains=query)
            )
        
        if estado == 'activas':
            motos = motos.filter(activo=True)
        elif estado == 'inactivas':
            motos = motos.filter(activo=False)

    context = {
        'motos': motos,
        'form': form,
    }
    return render(request, 'moto/listar.html', context)

@login_required
def crear_moto(request):
    """Crea una nueva moto"""
    if request.method == 'POST':
        form = MotoForm(request.POST, request.FILES)
        if form.is_valid():
            moto = form.save(commit=False)
            moto.creado_por = request.user
            moto.save()
            messages.success(request, f'Moto {moto.patente} creada exitosamente.')
            return redirect('moto:listar')
    else:
        form = MotoForm()

    context = {'form': form}
    return render(request, 'moto/form_moto.html', context)

@login_required
def editar_moto(request, patente):
    """Edita una moto existente"""
    moto = get_object_or_404(Moto, patente=patente)
    
    if request.method == 'POST':
        form = MotoForm(request.POST, request.FILES, instance=moto)
        if form.is_valid():
            moto_editada = form.save(commit=False)
            moto_editada.modificado_por = request.user
            moto_editada.save()
            messages.success(request, f'Moto {moto_editada.patente} actualizada exitosamente.')
            return redirect('moto:listar')
    else:
        form = MotoForm(instance=moto)

    context = {'form': form, 'moto': moto}
    return render(request, 'moto/form_moto.html', context)

@login_required
def eliminar_moto(request, patente):
    """Eliminación suave de una moto"""
    moto = get_object_or_404(Moto, patente=patente)
    
    if request.method == 'POST':
        moto.soft_delete()
        messages.success(request, f'Moto {moto.patente} desactivada exitosamente.')
        return redirect('moto:listar')
    
    context = {'moto': moto}
    return render(request, 'moto/confirmar_eliminar.html', context)

@login_required
def reactivar_moto(request, patente):
    """Reactiva una moto previamente desactivada"""
    moto = get_object_or_404(Moto, patente=patente)
    
    if request.method == 'POST':
        moto.reactivar()
        messages.success(request, f'Moto {moto.patente} reactivada exitosamente.')
        return redirect('moto:listar')
    
    context = {'moto': moto}
    return render(request, 'moto/confirmar_reactivar.html', context)

@login_required
def detalle_moto(request, patente):
    """Muestra el detalle completo de una moto"""
    moto = get_object_or_404(Moto, patente=patente)
    context = {'moto': moto}
    return render(request, 'moto/detalle.html', context)
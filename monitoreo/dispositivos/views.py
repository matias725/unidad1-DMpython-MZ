from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from .forms import DispositivoForm, RegistroEmpresaForm
from .models import Empresa, Zona, Dispositivo, Medicion

# ==========================
# DASHBOARD
# ==========================
@login_required
def dashboard(request):
    # Traer las últimas 10 mediciones recientes
    mediciones = Medicion.objects.select_related('dispositivo').order_by('-fecha')[:10]

    # Contar dispositivos por zona
    zonas = Zona.objects.annotate(num_dispositivos=Count('dispositivo'))

    # Inicializar listas para alertas según consumo
    alertas_grave = []
    alertas_alta = []
    alertas_media = []

    for medicion in mediciones:
        consumo = medicion.consumo
        if consumo >= 100:
            alertas_grave.append(medicion)
        elif consumo > 80:
            alertas_alta.append(medicion)
        elif consumo > 60:
            alertas_media.append(medicion)
        # Consumos ≤60 no generan alerta

    return render(request, 'dispositivos/panel.html', {
        'mediciones': mediciones,
        'zonas': zonas,
        'alertas_grave': alertas_grave,
        'alertas_alta': alertas_alta,
        'alertas_media': alertas_media,
    })


# ==========================
# REGISTRO DE EMPRESA
# ==========================
def registro_empresa(request):
    if request.method == 'POST':
        form = RegistroEmpresaForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['usuario']).exists():
                form.add_error('usuario', 'Este usuario ya existe')
            else:
                usuario = User.objects.create_user(
                    username=form.cleaned_data['usuario'],
                    password=form.cleaned_data['password']
                )
                Empresa.objects.create(
                    usuario=usuario,
                    nombre=form.cleaned_data['nombre']
                )
                login(request, usuario)
                return redirect('dashboard')
    else:
        form = RegistroEmpresaForm()
    return render(request, 'dispositivos/registro.html', {'form': form})


# ==========================
# DISPOSITIVOS
# ==========================
@login_required
def listar_dispositivos(request):
    categoria = request.GET.get('categoria')
    dispositivos = Dispositivo.objects.all()
    if categoria:
        dispositivos = dispositivos.filter(categoria=categoria)
    return render(request, 'dispositivos/dispositivo_list.html', {'dispositivos': dispositivos})


@login_required
def detalle_dispositivo(request, dispositivo_id):
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id)
    mediciones = Medicion.objects.filter(dispositivo=dispositivo).order_by('-fecha')
    
    # Calcular alertas de este dispositivo según consumo
    alertas_grave = []
    alertas_alta = []
    alertas_media = []
    for medicion in mediciones:
        if medicion.consumo >= 100:
            alertas_grave.append(medicion)
        elif medicion.consumo > 80:
            alertas_alta.append(medicion)
        elif medicion.consumo > 60:
            alertas_media.append(medicion)

    return render(request, 'dispositivos/dispositivo_detalle.html', {
        'dispositivo': dispositivo,
        'mediciones': mediciones,
        'alertas_grave': alertas_grave,
        'alertas_alta': alertas_alta,
        'alertas_media': alertas_media,
    })


@login_required
def crear_dispositivo(request):
    if request.method == "POST":
        form = DispositivoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("listar_dispositivos")
    else:
        form = DispositivoForm()
    return render(request, "dispositivos/dispositivo_form.html", {"form": form})


@login_required
def editar_dispositivo(request, dispositivo_id):
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id)
    if request.method == "POST":
        form = DispositivoForm(request.POST, instance=dispositivo)
        if form.is_valid():
            form.save()
            return redirect("detalle_dispositivo", dispositivo_id=dispositivo.id)
    else:
        form = DispositivoForm(instance=dispositivo)
    return render(request, "dispositivos/dispositivo_form.html", {"form": form})


@login_required
def eliminar_dispositivo(request, dispositivo_id):
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id)
    if request.method == "POST":
        dispositivo.delete()
        return redirect("listar_dispositivos")
    return render(request, "dispositivos/dispositivo_confirm_delete.html", {"dispositivo": dispositivo})


# ==========================
# MEDICIONES
# ==========================
@login_required
def listar_mediciones(request):
    mediciones = Medicion.objects.select_related('dispositivo').order_by('-fecha')
    return render(request, 'dispositivos/mediciones_list.html', {
        'mediciones': mediciones
    })


# ==========================
# PANEL CONSUMO DEMO
# ==========================
@login_required
def panel_consumo(request):
    dispositivos = [
        {"nombre": "Sensor Temperatura", "consumo": 50},
        {"nombre": "Medidor Solar", "consumo": 120},
        {"nombre": "Sensor Movimiento", "consumo": 30},
        {"nombre": "Calefactor", "consumo": 200},
    ]
    consumo_maximo = 100
    return render(request, "dispositivos/panel_consumo.html", {
        "dispositivos": dispositivos,
        "consumo_maximo": consumo_maximo
    })


@login_required
def inicio(request):
    dispositivos = Dispositivo.objects.all()
    return render(request, "dispositivos/inicio.html", {"dispositivos": dispositivos})






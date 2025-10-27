from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, Http404 
from django.views.decorators.http import require_POST
from django.db.models import Count, Q  
from django.core.paginator import Paginator 
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from .forms import DispositivoForm, RegistroEmpresaForm, ZonaForm
from .models import Empresa, Zona, Dispositivo, Medicion

# ==========================
# FUNCIÓN DE AYUDA (Helper)
# ==========================
def get_empresa_del_usuario(user):
    if user.is_superuser:
        return None 
    try:
        return user.empresa
    except ObjectDoesNotExist:
        raise Http404("El usuario no está asociado a ninguna empresa.")

# ==========================
# DASHBOARD
# ==========================
@login_required
def dashboard(request):
    empresa_usuario = get_empresa_del_usuario(request.user)
    
    mediciones_qs = Medicion.objects.select_related('dispositivo')
    zonas_qs = Zona.objects.all()

    if empresa_usuario:
        mediciones_qs = mediciones_qs.filter(dispositivo__zona__empresa=empresa_usuario)
        zonas_qs = zonas_qs.filter(empresa=empresa_usuario)

    mediciones = mediciones_qs.order_by('-fecha')[:10]
    zonas = zonas_qs.annotate(num_dispositivos=Count('dispositivo'))

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
@permission_required('dispositivos.view_dispositivo', raise_exception=True) 
def listar_dispositivos(request):
    
    empresa_usuario = get_empresa_del_usuario(request.user)
    q = request.GET.get('q', '').strip() 
    sort = request.GET.get('sort', 'nombre') 
    categoria = request.GET.get('categoria') 
    page_number = request.GET.get('page') 
    size = request.GET.get('size', '10') 

    try:
        page_size = int(size)
    except ValueError:
        page_size = 10

    qs = Dispositivo.objects.select_related('zona').all()
    
    if empresa_usuario:
        qs = qs.filter(zona__empresa=empresa_usuario)

    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) |
            Q(categoria__icontains=q) |
            Q(zona__nombre__icontains=q)
        ) 

    if categoria:
        qs = qs.filter(categoria=categoria)
    
    qs = qs.order_by(sort) 

    paginator = Paginator(qs, page_size) 
    page_obj = paginator.get_page(page_number) 

    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    querystring = params.urlencode() 
    
    context = {
        'page_obj': page_obj,       
        'q': q,
        'sort': sort,
        'categoria': categoria,
        'querystring': querystring,
        'size': size 
    }
    
    return render(request, 'dispositivos/dispositivo_list.html', context)


@login_required
@permission_required('dispositivos.view_dispositivo', raise_exception=True) 
def detalle_dispositivo(request, dispositivo_id):
    empresa_usuario = get_empresa_del_usuario(request.user)
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id)
    
    if empresa_usuario and dispositivo.zona.empresa != empresa_usuario:
        raise Http404("Dispositivo no encontrado.")

    mediciones = Medicion.objects.filter(dispositivo=dispositivo).order_by('-fecha')
    
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
@permission_required('dispositivos.add_dispositivo', raise_exception=True) 
def crear_dispositivo(request):
    if request.method == "POST":
        form = DispositivoForm(request.POST, user=request.user)
        if form.is_valid():
            zona_seleccionada = form.cleaned_data['zona']
            empresa_usuario = get_empresa_del_usuario(request.user)
            
            if empresa_usuario and zona_seleccionada.empresa != empresa_usuario:
                form.add_error('zona', 'Esta zona no pertenece a tu empresa.')
            else:
                form.save()
                return redirect("listar_dispositivos")
    else:
        form = DispositivoForm(user=request.user)
    
    return render(request, "dispositivos/dispositivo_form.html", {"form": form})


@login_required
@permission_required('dispositivos.change_dispositivo', raise_exception=True) 
def editar_dispositivo(request, dispositivo_id):
    empresa_usuario = get_empresa_del_usuario(request.user)
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id)

    if empresa_usuario and dispositivo.zona.empresa != empresa_usuario:
        raise Http404("Dispositivo no encontrado.")

    if request.method == "POST":
        form = DispositivoForm(request.POST, instance=dispositivo, user=request.user)
        if form.is_valid():
            zona_seleccionada = form.cleaned_data['zona']
            if empresa_usuario and zona_seleccionada.empresa != empresa_usuario:
                form.add_error('zona', 'Esta zona no pertenece a tu empresa.')
            else:
                form.save()
                return redirect("detalle_dispositivo", dispositivo_id=dispositivo.id)
    else:
        form = DispositivoForm(instance=dispositivo, user=request.user)
    
    return render(request, "dispositivos/dispositivo_form.html", {"form": form})


@login_required
@permission_required('dispositivos.delete_dispositivo', raise_exception=True) 
@require_POST 
def eliminar_dispositivo(request, dispositivo_id):
    empresa_usuario = get_empresa_del_usuario(request.user)
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id)

    if empresa_usuario and dispositivo.zona.empresa != empresa_usuario:
        return JsonResponse({"ok": False, "message": "Permiso denegado."}, status=403)

    try:
        nombre = dispositivo.nombre
        dispositivo.delete()
        return JsonResponse({"ok": True, "message": f"Dispositivo '{nombre}' eliminado"})
    except Exception as e:
        return JsonResponse({"ok": False, "message": str(e)}, status=400)

# ==========================
# ZONAS
# ==========================

@login_required
@permission_required('dispositivos.view_zona', raise_exception=True) 
def listar_zonas(request):
    empresa_usuario = get_empresa_del_usuario(request.user)
    
    zonas_qs = Zona.objects.all()
    if empresa_usuario:
        zonas_qs = zonas_qs.filter(empresa=empresa_usuario)
    
    zonas = zonas_qs.annotate(num_dispositivos=Count('dispositivo')).order_by('nombre')
    
    return render(request, 'dispositivos/zona_list.html', {'zonas': zonas})


@login_required
@permission_required('dispositivos.add_zona', raise_exception=True) 
def crear_zona(request):
    empresa_usuario = get_empresa_del_usuario(request.user)

    if not empresa_usuario:
        raise PermissionDenied("Los administradores deben gestionar las zonas desde el panel /admin/")

    if request.method == 'POST':
        form = ZonaForm(request.POST)
        if form.is_valid():
            zona = form.save(commit=False)
            zona.empresa = empresa_usuario 
            zona.save()
            return redirect('listar_zonas')
    else:
        form = ZonaForm()
        
    return render(request, "dispositivos/zona_form.html", {"form": form})


@login_required
@permission_required('dispositivos.change_zona', raise_exception=True) 
def editar_zona(request, zona_id):
    empresa_usuario = get_empresa_del_usuario(request.user)
    
    qs = Zona.objects.all()
    if empresa_usuario:
        qs = qs.filter(empresa=empresa_usuario) 
        
    zona = get_object_or_404(qs, id=zona_id)
    
    if request.method == 'POST':
        form = ZonaForm(request.POST, instance=zona)
        if form.is_valid():
            form.save()
            return redirect('listar_zonas')
    else:
        form = ZonaForm(instance=zona)
        
    return render(request, "dispositivos/zona_form.html", {"form": form, "zona": zona})


@login_required
@permission_required('dispositivos.delete_zona', raise_exception=True) 
@require_POST
def eliminar_zona(request, zona_id):
    empresa_usuario = get_empresa_del_usuario(request.user)
    
    qs = Zona.objects.all()
    if empresa_usuario:
        qs = qs.filter(empresa=empresa_usuario) 
        
    zona = get_object_or_404(qs, id=zona_id)
    
    if zona.dispositivo_set.count() > 0:
        return JsonResponse({"ok": False, "message": "No se puede eliminar la zona porque tiene dispositivos asociados."}, status=400)
    
    try:
        nombre = zona.nombre
        zona.delete()
        return JsonResponse({"ok": True, "message": f"Zona '{nombre}' eliminada"})
    except Exception as e:
        return JsonResponse({"ok": False, "message": str(e)}, status=400)


# ==========================
# MEDICIONES (¡MODIFICADO!)
# ==========================
@login_required
@permission_required('dispositivos.view_medicion', raise_exception=True) 
def listar_mediciones(request):
    empresa_usuario = get_empresa_del_usuario(request.user)

    # --- 1. Obtener parámetros de Filtro y Paginación ---
    dispositivo_id = request.GET.get('dispositivo_id', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    page_number = request.GET.get('page') 
    size = request.GET.get('size', '10')

    try:
        page_size = int(size)
    except ValueError:
        page_size = 10

    # --- 2. Queryset Base de Mediciones (filtrado por empresa) ---
    mediciones_qs = Medicion.objects.select_related('dispositivo', 'dispositivo__zona')
    if empresa_usuario:
        mediciones_qs = mediciones_qs.filter(dispositivo__zona__empresa=empresa_usuario)

    # --- 3. Queryset Base de Dispositivos (para el <select>) ---
    dispositivos_para_filtro = Dispositivo.objects.order_by('nombre')
    if empresa_usuario:
        dispositivos_para_filtro = dispositivos_para_filtro.filter(zona__empresa=empresa_usuario)

    # --- 4. Aplicar Filtros ---
    if dispositivo_id:
        mediciones_qs = mediciones_qs.filter(dispositivo_id=dispositivo_id)
    
    if fecha_inicio:
        # __date__gte compara solo la fecha (ignora la hora)
        mediciones_qs = mediciones_qs.filter(fecha__date__gte=fecha_inicio) 
    
    if fecha_fin:
        # __date__lte compara solo la fecha (ignora la hora)
        mediciones_qs = mediciones_qs.filter(fecha__date__lte=fecha_fin)

    # --- 5. Aplicar Orden y Paginación ---
    mediciones_qs = mediciones_qs.order_by('-fecha') # Más recientes primero
    paginator = Paginator(mediciones_qs, page_size) 
    page_obj = paginator.get_page(page_number) 

    # --- 6. QueryString para mantener filtros ---
    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    querystring = params.urlencode() 

    # --- 7. Contexto ---
    context = {
        'page_obj': page_obj,
        'querystring': querystring,
        'dispositivos_para_filtro': dispositivos_para_filtro,
        'dispositivo_id_seleccionado': dispositivo_id,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'size': size
    }
    
    return render(request, 'dispositivos/mediciones_list.html', context)


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

# ==========================
# INICIO
# ==========================
@login_required
def inicio(request):
    dispositivos = Dispositivo.objects.all()
    
    return render(request, "dispositivos/inicio.html", {"dispositivos": dispositivos})
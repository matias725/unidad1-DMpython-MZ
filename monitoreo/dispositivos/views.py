from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q  
from django.core.paginator import Paginator 
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib import messages
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from usuarios.decorators import admin_required, editor_required, lector_required

from .forms import DispositivoForm, RegistroEmpresaForm, ZonaForm, MedicionForm
from .models import Empresa, Zona, Dispositivo, Medicion, Alerta

def get_empresa_del_usuario(user):
    if user.is_superuser:
        return None 
    try:
        return user.empresa
    except (ObjectDoesNotExist, AttributeError):
        return None

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

@login_required
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
    
    # Guardar configuración de paginación en sesión
    if 'size' in request.GET:
        request.session['dispositivos_page_size'] = page_size
    elif 'dispositivos_page_size' in request.session:
        page_size = request.session['dispositivos_page_size']
    
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
        'size': str(page_size),
        'categorias': Dispositivo.CATEGORIAS
    }
    
    return render(request, 'dispositivos/dispositivo_list.html', context)

@login_required
def detalle_dispositivo(request, dispositivo_id):
    empresa_usuario = get_empresa_del_usuario(request.user)
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id)
    
    if empresa_usuario and dispositivo.zona.empresa != empresa_usuario:
        raise Http404("Dispositivo no encontrado.")

    mediciones = Medicion.objects.filter(dispositivo=dispositivo).order_by('-fecha')
    
    alertas_grave = Alerta.objects.filter(dispositivo=dispositivo, gravedad='Grave').order_by('-fecha')
    alertas_alta = Alerta.objects.filter(dispositivo=dispositivo, gravedad='Alta').order_by('-fecha')
    alertas_media = Alerta.objects.filter(dispositivo=dispositivo, gravedad='Media').order_by('-fecha')

    return render(request, 'dispositivos/dispositivo_detalle.html', {
        'dispositivo': dispositivo,
        'mediciones': mediciones,
        'alertas_grave': alertas_grave,
        'alertas_alta': alertas_alta,
        'alertas_media': alertas_media,
    })

@login_required
@editor_required
def crear_dispositivo(request):
    if request.method == "POST":
        form = DispositivoForm(request.POST, user=request.user)
        if form.is_valid():
            zona_seleccionada = form.cleaned_data['zona']
            empresa_usuario = get_empresa_del_usuario(request.user)
            
            if empresa_usuario and zona_seleccionada.empresa != empresa_usuario:
                form.add_error('zona', 'Esta zona no pertenece a tu empresa.')
            else:
                dispositivo = form.save()
                messages.success(request, f'Dispositivo "{dispositivo.nombre}" creado exitosamente.')
                return redirect("dispositivos:dispositivo_list")
    else:
        form = DispositivoForm(user=request.user)
    
    return render(request, "dispositivos/dispositivo_form.html", {"form": form})

@login_required
@editor_required
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
                dispositivo = form.save()
                messages.success(request, f'Dispositivo "{dispositivo.nombre}" actualizado exitosamente.')
                return redirect("dispositivos:dispositivo_detail", dispositivo_id=dispositivo.id)
    else:
        form = DispositivoForm(instance=dispositivo, user=request.user)
    
    return render(request, "dispositivos/dispositivo_form.html", {"form": form})

@login_required
@admin_required
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

@login_required
def listar_zonas(request):
    empresa_usuario = get_empresa_del_usuario(request.user)
    
    zonas_qs = Zona.objects.all()
    if empresa_usuario:
        zonas_qs = zonas_qs.filter(empresa=empresa_usuario)
    
    zonas = zonas_qs.annotate(num_dispositivos=Count('dispositivo')).order_by('nombre')
    
    return render(request, 'dispositivos/zona_list.html', {'zonas': zonas})

@login_required
def crear_zona(request):
    empresa_usuario = get_empresa_del_usuario(request.user)

    if request.method == 'POST':
        form = ZonaForm(request.POST)
        if form.is_valid():
            zona = form.save(commit=False)
            if empresa_usuario:
                zona.empresa = empresa_usuario
            else:
                # Crear empresa por defecto para superusuarios
                from django.contrib.auth.models import User
                admin_user = User.objects.filter(is_superuser=True).first()
                empresa, created = Empresa.objects.get_or_create(
                    usuario=admin_user,
                    defaults={'nombre': 'EcoEnergy'}
                )
                zona.empresa = empresa
            zona.save()
            messages.success(request, f'Zona "{zona.nombre}" creada exitosamente.')
            return redirect('dispositivos:zona_list')
    else:
        form = ZonaForm()
        
    return render(request, "dispositivos/zona_form.html", {"form": form})

@login_required
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
            messages.success(request, f'Zona "{zona.nombre}" actualizada exitosamente.')
            return redirect('dispositivos:zona_list')
    else:
        form = ZonaForm(instance=zona)
        
    return render(request, "dispositivos/zona_form.html", {"form": form, "zona": zona})

@login_required
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

@login_required
def listar_mediciones(request):
    empresa_usuario = get_empresa_del_usuario(request.user)

    dispositivo_id = request.GET.get('dispositivo_id', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    page_number = request.GET.get('page') 
    size = request.GET.get('size', '10')

    try:
        page_size = int(size)
    except ValueError:
        page_size = 10

    mediciones_qs = Medicion.objects.select_related('dispositivo', 'dispositivo__zona')
    if empresa_usuario:
        mediciones_qs = mediciones_qs.filter(dispositivo__zona__empresa=empresa_usuario)

    dispositivos_para_filtro = Dispositivo.objects.order_by('nombre')
    if empresa_usuario:
        dispositivos_para_filtro = dispositivos_para_filtro.filter(zona__empresa=empresa_usuario)

    if dispositivo_id:
        mediciones_qs = mediciones_qs.filter(dispositivo_id=dispositivo_id)
    
    if fecha_inicio:
        try:
            mediciones_qs = mediciones_qs.filter(fecha__date__gte=fecha_inicio)
        except:
            fecha_inicio = ''
    
    if fecha_fin:
        try:
            mediciones_qs = mediciones_qs.filter(fecha__date__lte=fecha_fin)
        except:
            fecha_fin = ''

    mediciones_qs = mediciones_qs.order_by('-fecha')
    paginator = Paginator(mediciones_qs, page_size) 
    page_obj = paginator.get_page(page_number) 

    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    querystring = params.urlencode() 

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

@login_required
def listar_alertas(request):
    empresa_usuario = get_empresa_del_usuario(request.user)

    dispositivo_id = request.GET.get('dispositivo_id', '')
    gravedad = request.GET.get('gravedad', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    page_number = request.GET.get('page') 
    size = request.GET.get('size', '10')

    try:
        page_size = int(size)
    except ValueError:
        page_size = 10
    
    alertas_qs = Alerta.objects.select_related('dispositivo', 'dispositivo__zona')
    if empresa_usuario:
        alertas_qs = alertas_qs.filter(dispositivo__zona__empresa=empresa_usuario)

    dispositivos_para_filtro = Dispositivo.objects.order_by('nombre')
    if empresa_usuario:
        dispositivos_para_filtro = dispositivos_para_filtro.filter(zona__empresa=empresa_usuario)

    if dispositivo_id:
        alertas_qs = alertas_qs.filter(dispositivo_id=dispositivo_id)
    
    if gravedad:
        alertas_qs = alertas_qs.filter(gravedad=gravedad)
    
    if fecha_inicio:
        try:
            alertas_qs = alertas_qs.filter(fecha__date__gte=fecha_inicio)
        except:
            fecha_inicio = ''
    
    if fecha_fin:
        try:
            alertas_qs = alertas_qs.filter(fecha__date__lte=fecha_fin)
        except:
            fecha_fin = ''

    alertas_qs = alertas_qs.order_by('-fecha')
    paginator = Paginator(alertas_qs, page_size) 
    page_obj = paginator.get_page(page_number) 

    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    querystring = params.urlencode() 

    context = {
        'page_obj': page_obj,
        'querystring': querystring,
        'dispositivos_para_filtro': dispositivos_para_filtro,
        'dispositivo_id_seleccionado': dispositivo_id,
        'gravedad_seleccionada': gravedad,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'size': size,
        'GRAVEDAD_CHOICES': Alerta.GRAVEDAD_CHOICES
    }
    
    return render(request, 'dispositivos/alertas_list.html', context)

@login_required
def exportar_dispositivos_excel(request):
    empresa_usuario = get_empresa_del_usuario(request.user)
    
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria')
    
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
    
    qs = qs.order_by('nombre')
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Dispositivos"
    
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
    headers = ['ID', 'Nombre', 'Categoría', 'Zona', 'Empresa', 'Watts']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
    
    for row, dispositivo in enumerate(qs, 2):
        ws.cell(row=row, column=1, value=dispositivo.id)
        ws.cell(row=row, column=2, value=dispositivo.nombre)
        ws.cell(row=row, column=3, value=dispositivo.categoria)
        ws.cell(row=row, column=4, value=dispositivo.zona.nombre if dispositivo.zona else 'Sin zona')
        ws.cell(row=row, column=5, value=dispositivo.zona.empresa.nombre if dispositivo.zona else 'Sin empresa')
        ws.cell(row=row, column=6, value=dispositivo.watts)
    
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="dispositivos.xlsx"'
    
    wb.save(response)
    return response

@login_required
def detalle_medicion(request, medicion_id):
    medicion = get_object_or_404(Medicion, id=medicion_id)
    return render(request, 'dispositivos/medicion_detalle.html', {'medicion': medicion})

@login_required
def crear_medicion(request):
    if request.method == 'POST':
        form = MedicionForm(request.POST, user=request.user)
        if form.is_valid():
            medicion = form.save()
            messages.success(request, f'Medición creada exitosamente para {medicion.dispositivo.nombre}.')
            return redirect('dispositivos:medicion_list')
    else:
        form = MedicionForm(user=request.user)
    
    return render(request, 'dispositivos/medicion_form.html', {'form': form})

@login_required
def editar_medicion(request, medicion_id):
    medicion = get_object_or_404(Medicion, id=medicion_id)
    
    if request.method == 'POST':
        form = MedicionForm(request.POST, instance=medicion, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medición actualizada exitosamente.')
            return redirect('dispositivos:medicion_list')
    else:
        form = MedicionForm(instance=medicion, user=request.user)
    
    return render(request, 'dispositivos/medicion_form.html', {'form': form, 'medicion': medicion})

@login_required
@require_POST
def eliminar_medicion(request, medicion_id):
    medicion = get_object_or_404(Medicion, id=medicion_id)
    
    try:
        dispositivo_nombre = medicion.dispositivo.nombre
        medicion.delete()
        return JsonResponse({"ok": True, "message": f"Medición de {dispositivo_nombre} eliminada"})
    except Exception as e:
        return JsonResponse({"ok": False, "message": str(e)}, status=400)

def custom_404(request, exception):
    return render(request, '404.html', status=404)
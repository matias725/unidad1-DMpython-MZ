from django.shortcuts import render
from django.http import JsonResponse

def info(request):
    datos = {
        "proyecto": "EcoEnergy",
        "version": "1.0",
        "autor": "matias"  # <--- ¡Pon tu nombre aquí!
    }
    return JsonResponse(datos)
# Create your views here.

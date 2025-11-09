from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from usuarios.models import Organizacion

class Zona(models.Model):
    nombre = models.CharField(max_length=100)
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['nombre', 'organizacion']

    def __str__(self):
        return f"{self.nombre} ({self.organizacion.nombre})"

class Dispositivo(models.Model):
    CATEGORIAS = [
        ("Sensor", "Sensor"),
        ("Actuador", "Actuador"),
        ("General", "General"),
    ]
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default="General")
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE, null=True, blank=True)
    watts = models.FloatField(help_text="Consumo nominal en watts", default=0)

    def clean(self):
        if self.watts < 0:
            raise ValidationError("El consumo en watts no puede ser un número negativo.")

    def __str__(self):
        return f"{self.nombre} - {self.categoria} ({self.watts}W)"

class Medicion(models.Model):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    consumo = models.FloatField(help_text="Consumo en kWh")

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.dispositivo.nombre}: {self.consumo} kWh ({self.fecha.strftime('%Y-%m-%d %H:%M')})"

class Alerta(models.Model):
    GRAVEDAD_CHOICES = [
        ('Grave', 'Grave'),
        ('Alta', 'Alta'),
        ('Media', 'Media'),
    ]
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    mensaje = models.CharField(max_length=200)
    gravedad = models.CharField(max_length=10, choices=GRAVEDAD_CHOICES)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"[{self.gravedad}] {self.mensaje} - {self.dispositivo.nombre}"
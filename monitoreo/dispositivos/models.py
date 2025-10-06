from django.db import models
from django.contrib.auth.models import User


class Empresa(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Zona(models.Model):
    nombre = models.CharField(max_length=100)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} ({self.empresa.nombre})"


class Dispositivo(models.Model):
    CATEGORIAS = [
        ("Sensor", "Sensor"),
        ("Actuador", "Actuador"),
        ("General", "General"),
    ]
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default="General")
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE, null=True, blank=True)
    watts = models.FloatField(help_text="Consumo nominal en watts", default=0)  # 👈 nuevo campo

    def __str__(self):
        return f"{self.nombre} - {self.categoria} ({self.watts}W)"



class Medicion(models.Model):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    consumo = models.FloatField(help_text="Consumo en kWh")

    class Meta:
        ordering = ['-fecha']  # siempre mostrar las más recientes primero

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



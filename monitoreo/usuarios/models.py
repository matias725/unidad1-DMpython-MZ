from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Organizacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Organizaciones"

class Perfil(models.Model):
    ROLES = [
        ('cliente_admin', 'Cliente Admin'),
        ('cliente_electronico', 'Cliente Electrónico'),
        ('encargado_ecoenergy', 'Encargado EcoEnergy'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(blank=True, null=True, upload_to='avatars/')
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente_electronico')
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Perfil de {self.user.username} - {self.get_rol_display()}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Redimensionar imagen si es muy grande y existe
        if self.avatar and hasattr(self.avatar, 'path'):
            try:
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except (FileNotFoundError, OSError):
                pass
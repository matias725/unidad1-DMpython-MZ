from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(blank=True, null=True, upload_to='avatars/')
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
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
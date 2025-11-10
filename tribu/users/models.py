from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        related_name='profile', 
        on_delete=models.CASCADE
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to='avatars', 
        default='avatars/noavatar.png'
    )
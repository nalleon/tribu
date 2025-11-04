from django.db import models
from django.conf import settings

class Wave(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='waves' 
    )

    echo = models.ForeignKey(
        'echos.Echo',
        related_name='waves',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )


    def __str__(self):
        return f'Pk: {self.pk}'

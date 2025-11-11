from django.conf import settings
from django.db import models


class Echo(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='echos' 
    )

    def __str__(self):
        return f'Pk: {self.pk}'
    
    class Meta:
        ordering = ['-created_at']

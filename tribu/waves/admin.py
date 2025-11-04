from django.contrib import admin

from .models import Wave

@admin.register(Wave)
class WaveAdmin(admin.ModelAdmin):
    list_display = ('pk', 'content', 'created_at', 'updated_at', 'user', 'echo')
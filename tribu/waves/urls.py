from django.urls import path
from . import views

app_name = 'waves'


urlpatterns = [
    path('<int:wave_pk>/edit/', views.edit_wave, name='edit-wave'),
    path('<int:wave_pk>/delete/', views.delete_wave, name='delete-wave'),
]
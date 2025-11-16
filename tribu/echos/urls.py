from django.urls import path  #, register_converter

from . import views  #, converters

app_name = 'echos'
# register_converter(converters.PostConverter, 'echo')


urlpatterns = [
    path('', views.echo_list, name='echo-list'),
    path('add/', views.add_echo, name='add-echo'),
    path('<int:echo_pk>/', views.echo_detail, name='echo-detail'),
    path('<int:echo_pk>/waves/', views.echo_waves, name='echo-waves'),
    path('<int:echo_pk>/waves/add/', views.add_wave, name='add-wave'),
    path('<int:echo_pk>/delete/', views.delete_echo, name='delete-echo'),
    path('<int:echo_pk>/edit/', views.edit_echo, name='edit-echo'),
]
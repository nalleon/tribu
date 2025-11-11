from django.urls import path  #, register_converter

from . import views  #, converters

app_name = 'echos'
# register_converter(converters.PostConverter, 'echo')


urlpatterns = [
    path('', views.echo_list, name='echo-list'),
    path('add/', views.add_echo, name='add-echo'),
    # path('<post:post>/delete/', views.delete_post, name='delete-post'),
    path('<int:echo_pk>/', views.echo_detail, name='echo-detail'),
    # path('<post:post>/edit/', views.edit_post, name='edit-post'),
]
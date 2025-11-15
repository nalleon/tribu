from django.urls import path
from . import views

app_name = 'waves'


urlpatterns = [
    path('<int:echo_pk>/waves/', views.echo_waves, name='echo-waves'),
    # path('<post:post>/edit/', views.edit_post, name='edit-post'),
]
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('', views.user_list, name='user-list'),
    path('<username>/', views.user_detail, name='profile'),
    path('<username>/echos', views.user_echos, name='user-echos'),
    path('@me/', views.my_user_detail, name='me'),
    path('<username>/edit', views.edit_profile, name='user-edit')
]
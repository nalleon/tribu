from django.urls import path

from . import views

urlpatterns = [
    path('', views.user_list, name='user-list'),
    path('<username>/', views.user_detail, name='profile'),
    path('<username>/echos', views.user_echos, name='signup'),
    path('@me/', views.my_user_detail, name='signup'),
    path('<username>/edit', views.edit_profile, name='user-edit')
]
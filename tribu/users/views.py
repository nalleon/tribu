from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .models import Profile


def user_list(request):
    try:
        users = Profile.objects.all()

    except Profile.DoesNotExist:
        return HttpResponse('There are no Echos currently!')

    return render(request, 'users/list.html', {'users': users})

def user_details(request):

    return redirect('index')

def user_echos(request):

    return redirect('index')



@login_required
def profile_view(request):
    profile = request.user.profile
    posts = request.user.posts.all()
    return render(request, 'profile.html', {
        'profile': profile,
        'posts': posts
    })
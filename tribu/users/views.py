from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .models import Profile


@login_required

def user_list(request):
    try:
        users = Profile.objects.all()

    except Profile.DoesNotExist:
        return HttpResponse('There are no users currently!')

    return render(request, 'users/list.html', {'users': users})


@login_required
def user_detail(request, username):

    try:
        user = Profile.objects.get(username=username)
    except Profile.DoesNotExist:
        return HttpResponse('This user does not exist!')
    return render(request, 'users/profile/profile.html', {"users": user})

@login_required
def user_echos(request):

    return redirect('index')

@login_required
def my_user_detail(request):

    return redirect('index')

@login_required
def edit_profile(request):

    return redirect('index')

@login_required
def profile_view(request):
    profile = request.user.profile
    posts = request.user.posts.all()
    return render(request, 'profile.html', {
        'profile': profile,
        'posts': posts
    })
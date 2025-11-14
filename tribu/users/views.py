from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponseNotFound
from .models import Profile
from .forms import EditProfileForm


@login_required
def user_list(request):
    try:
        users = Profile.objects.all()
    except Profile.DoesNotExist:
        return HttpResponse('There are no users currently!')

    return render(request, 'users/list.html', {'profiles': users})


@login_required
def user_detail(request, username):
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        return HttpResponseNotFound(
            f"User with username '{username}' does not exist"
        )    
    return render(request, 'users/profile/profile.html', {'profile': profile})

@login_required
def user_echos(request, username):
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        return HttpResponseNotFound(
            f"User with username '{username}' does not exist"
        )    
    return render(request, 'users/profile/profile-echos.html', {'profile': profile})

@login_required
def my_user_detail(request):
    username = request.user.username
    return redirect('users:profile', username=username)

@login_required
def edit_profile(request, username):

    # if request.method == 'POST':
    #     if (form := EditProfileForm(request.POST, instance=profile)).is_valid():

    #         profile.save(profile.user)
    #         return redirect('profiles:profile-list')

    # else:
    #     form = EditProfileForm(instance=profile)

    return redirect('index')

@login_required
def profile_view(request):
    profile = request.user.profile
    profiles = request.user.profiles.all()
    return render(request, 'profile.html', {
        'profile': profile,
        'profiles': profiles
    })
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotFound
from .models import Profile
from .forms import EditProfileForm
from django.contrib import messages


@login_required
def user_list(request):
    try:
        users = Profile.objects.all()
    except Profile.DoesNotExist:
        return HttpResponse('There are no users currently!')

    return render(request, 'users/list.html', {'profiles': users})


@login_required
def user_detail(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    return render(request, 'users/profile/profile.html', {'profile': profile})

@login_required
def user_echos(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    return render(request, 'users/profile/profile-echos.html', {'profile': profile})

@login_required
def my_user_detail(request):
    username = request.user.username
    return redirect('users:profile', username=username)

@login_required
def edit_profile(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    
    if profile.user != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        if (form := EditProfileForm(request.POST,request.FILES, instance=profile)).is_valid():
            profile = form.save(commit=False)
            profile.save()
            messages.success(request, 'Profile updated successfully')  
        return redirect('users:me')
    else:
        form = EditProfileForm(instance=profile)
    return render(request, 'users/profile/edit.html', {'form': form})


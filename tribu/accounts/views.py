from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import LoginForm, SignupForm


def user_login(request):
    FALLBACK_REDIRECT = 'index'

    if request.user.is_authenticated:
        return redirect(reverse(FALLBACK_REDIRECT))
    if request.method == 'POST':
        if (form := LoginForm(request.POST)).is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if user := authenticate(request, username=username, password=password):
                login(request, user)
                return redirect(request.GET.get('next', reverse(FALLBACK_REDIRECT)))
            else:
                messages.error(request, 'Incorrect username or password')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    FALLBACK_REDIRECT = 'index'

    logout(request)

    return redirect(reverse(FALLBACK_REDIRECT))


def user_signup(request):
    FALLBACK_REDIRECT = 'index'

    if request.user.is_authenticated:
        return redirect(reverse(FALLBACK_REDIRECT))
    if request.method == 'POST':
        if (form := SignupForm(request.POST)).is_valid():
            user = form.save()
            login(request, user)

            return redirect(FALLBACK_REDIRECT)
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})
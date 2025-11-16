from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import PermissionDenied

from .forms import AddEchoForm
from .forms import EditEchoForm
from .forms import AddWaveForm

from .models import Echo
from django.contrib import messages

@login_required
def echo_list(request):
    try:
        echos = Echo.objects.all()
    except Echo.DoesNotExist:
        return HttpResponse('There are no Echos currently!')    
    return render(request, 'echos/list.html', {'echos': echos})

@login_required
def echo_detail(request, echo_pk):
    echo = get_object_or_404(Echo, pk=echo_pk)
    return render(request, 'echos/echo/detail.html', {'echo': echo})

@login_required
def echo_waves(request, echo_pk):
    echo = get_object_or_404(Echo, pk=echo_pk)
    return render(request, 'echos/echo/detail-waves.html', {'echo': echo})

@login_required
def add_echo(request):
    if request.method == 'POST':
        form = AddEchoForm(request.POST)
        if form.is_valid():
            echo = form.save(request.user)
            messages.success(request, 'Echo added successfully')  
            return redirect('echos:echo-detail', echo_pk=echo.pk)
    else:
        form = AddEchoForm()

    return render(request, 'echos/echo/add.html', {'form': form})


@login_required
def edit_echo(request, echo_pk):

    echo = get_object_or_404(Echo, pk=echo_pk)

    if echo.user != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        if (form := EditEchoForm(request.POST, instance=echo)).is_valid():
            echo = form.save(commit=False)
            echo.save()
            messages.success(request, 'Echo updated successfully')  
            return redirect('echos:echo-detail', echo_pk=echo.pk)
    else:
        form = EditEchoForm(instance=echo)
    return render(request, 'echos/echo/edit.html', {'form': form, 'echo':echo})

@login_required
def delete_echo(request, echo_pk):
    echo = get_object_or_404(Echo, pk=echo_pk)

    if echo.user != request.user:
        raise PermissionDenied
    echo.delete()
    messages.success(request, 'Echo deleted successfully')  
    
    return redirect('echos:echo-list')

@login_required
def add_wave(request, echo_pk):
    echo = get_object_or_404(Echo, pk=echo_pk)
    if request.method == 'POST':
        if (form := AddWaveForm(request.POST)).is_valid():
            wave = form.save(commit=False)
            wave.echo = echo
            wave.user = request.user
            wave.save()
            messages.success(request, 'Wave added successfully')  
            return redirect('echos:echo-detail', echo_pk=echo.pk)
    else:
        form = AddWaveForm()
    return render(request, 'echos/echo/add-wave.html', {'form': form, 'echo': echo})


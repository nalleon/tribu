from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EditWaveForm

from echos.models import Echo
from .models import Wave


@login_required
def edit_wave(request, wave_pk):
    wave = get_object_or_404(Wave, pk=wave_pk)
    if wave.user != request.user:
        raise PermissionDenied
        
    echo = wave.echo
    if request.method == 'POST':
        if (form := EditWaveForm(request.POST, instance=wave)).is_valid():
            wave = form.save(commit=False)
            wave.save()
            messages.success(request, 'Wave updated successfully')  
            return redirect('echos:echo-detail', echo_pk=echo.pk)
    else:
        form = EditWaveForm(instance=wave)
    return render(request, 'waves/wave/edit.html', {'form': form, 'echo':echo})


@login_required
def delete_wave(request, wave_pk):
    wave = get_object_or_404(Wave, pk=wave_pk)
    if wave.user != request.user:
        raise PermissionDenied
    
    echo_pk = wave.echo.pk
    wave.delete()
    messages.success(request, 'Wave deleted successfully')  

    return redirect('echos:echo-detail', echo_pk=echo_pk)

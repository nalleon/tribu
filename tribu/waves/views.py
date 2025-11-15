from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from echos.models import Echo
from .models import Wave


@login_required
def echo_waves(request, echo_pk):

    try:
        echo = Echo.objects.get(pk=echo_pk)

    except Echo.DoesNotExist:
        return HttpResponse('There is no echo with that key currently!')

    return render(request, 'waves/echo-waves.html', {'echo': echo})

@login_required
def echo_waves_add(request, echo_pk):

    # try:
    #     echo = Echo.objects.get(pk=echo_pk)

    # except Echo.DoesNotExist:
    #     return HttpResponse('There is no echo with that key currently!')

    # return render(request, 'waves/echo-waves-add.html', {'echo': echo})
    return redirect ('index')

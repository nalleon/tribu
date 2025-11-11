from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

# from .forms import AddEchoForm
# from .forms import EditEchoForm
from .models import Echo


@login_required
def echo_list(request):
    try:
        echos = Echo.objects.all()

    except Echo.DoesNotExist:
        return HttpResponse('There are no Echos currently!')    
    return render(request, 'echos/list.html', {'echos': echos})

@login_required
def echo_detail(request, pk):
    try:
        echo = Echo.objects.get(pk=pk)
    except Echo.DoesNotExist:
        return HttpResponse(f'Echo with id "{pk}" does not exist!')
    return render(request, 'echos/echo/detail.html', {'echo': echo})

@login_required
def add_echo(request):
    return render ('index.html')


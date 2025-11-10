from django.shortcuts import render
from django.http import HttpResponse

# from .forms import AddEchoForm
# from .forms import EditEchoForm
from .models import Echo

def echo_list(request):
    try:
        echos = Echo.objects.all()

    except Echo.DoesNotExist:
        return HttpResponse('There are no Echos currently!')
    
    # print(f'{request.user=}')
    
    return render(request, 'echos/list.html', {'echos': echos})

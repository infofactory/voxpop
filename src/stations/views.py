from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic.list import ListView
from .models import *

# Create your views here.
def index(request):
    stations = Stop.objects.filter(location_type=1)

    context = {'stations':stations}
    return render(request, 'stations/stations.html', context)

def station_detail(request, id):
    from .forms import StopForm
    station = Stop.objects.get(pk=id)
    children = station.children.all()


    locations = [
        {'type':type_id, 'name':type_name, 'items':children.filter(location_type=type_id)}
        for type_id, type_name in Stop.LOCATION_TYPES if type_id != 1
    ]


    print(locations)

    context = {'station':station, 'locations':locations}
    return render(request, 'stations/detail.html', context)


def station_edit(request, id=None, parent=None):
    from .forms import StopForm
    if id:
        station = Stop.objects.get(pk=id)
    elif parent:
        station = Stop(parent_station_id=parent)
    else:
        station = None

    print(station)
    form = StopForm(request.POST or None, instance=station)

    if request.method == 'POST':
        if 'delete' in request.POST:
            station.delete()
            return redirect(reverse('station_detail', args=[station.parent_station.pk]))
        if form.is_valid():
            station = form.save()
            return redirect(reverse('station_detail', args=[station.pk]))
            

    context = {'station':station, 'form':form}
    return render(request, 'stations/edit.html', context)
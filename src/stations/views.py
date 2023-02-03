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
    lifts = station.lifts.all()

    if station.location_type == 1:
        locations = [
            {'type':type_id, 'name':type_name, 'items':children.filter(location_type=type_id)}
            for type_id, type_name in Stop.LOCATION_TYPES if type_id not in [station.location_type, 1 and 4]
        ]
        lift_list = [
            {'type':type_id, 'name':type_name, 'items':lifts.filter(type=type_id)}
            for type_id, type_name in Lift.LIFT_TYPES
        ]
    elif station.location_type == 0:
        locations = [
            {'type':type_id, 'name':type_name, 'items':children.filter(location_type=type_id)}
            for type_id, type_name in Stop.LOCATION_TYPES if type_id == 4
        ]
        lift_list = []
    else:
        locations = []
        lift_list = []

    if locations:
        for group in locations:
            if group['name'] == 'Area' and not group['items']:
                areas = False
            else:
                areas = True
    else:
        areas = None


    context = {'station':station, 'locations':locations, 'lift_list':lift_list, 'areas': areas}
    return render(request, 'stations/details.html', context)


def station_edit(request, id=None, parent=None):
    from .forms import StopForm
    if id:
        station = Stop.objects.get(pk=id)
    elif parent:
        station = Stop(parent_station_id=parent)
        station.location_type = int(request.GET.get('loc_type'))
    else:
        station = None

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

def lift_detail(request, id):
    lift = Lift.objects.get(pk=id)

    context= {'lift': lift}
    return render(request, 'lifts/details.html', context)


def lift_edit(request, id=None, parent=None):
    from .forms import LiftForm
    if id:
        lift = Lift.objects.get(pk=id)
    elif parent:
        lift_type = int(request.GET.get('type'))
        lift = Lift(stop_id_id=parent, type = lift_type)
    else:
        lift = None

    form = LiftForm(request.POST or None, instance=lift)

    if request.POST:
        if 'delete' in request.POST:
            parent = lift.stop_id.pk
            lift.delete()
            return redirect(reverse('station_detail', args=[parent]))
        if form.is_valid():
            lift = form.save()
            return redirect(reverse('lift_detail', args=[lift.pk]))

    context={'form':form, 'lift': lift}
    return render(request, 'lifts/edit.html',context)


def services_edit(request, platform=None, id=None):
    from .forms import ServicesForm
    # if platform add services
    if platform:
        parent = Stop.objects.get(id = platform)
        services = Services(platform_id = parent)
        form = ServicesForm(request.POST or None, instance=services)
    # if id edit services
    elif id:
        services = Services.objects.get(pk = id)
        form = ServicesForm(request.POST or None, instance=services)
    
    if request.POST:
        if 'delete' in request.POST:
            parent_platform = services.platform_id
            services.delete()
            return redirect(reverse('station_detail', args=[parent_platform]))
        if form.is_valid():
            services = form.save()
            return redirect(reverse('station_detail', args=[services.platform_id.pk]))

    context = {'form': form}
    return render(request, 'stations/services/edit.html', context)
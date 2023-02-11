from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.generic.list import ListView
from .models import *

from django.contrib.auth.decorators import login_required

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

    #areas = station.children.filter(location_type=5)

    #da rifinire e spostarkìla nei models: crea in automatico i level path
    # same = [areas.filter(level = a.level) for a in areas]
    # for area in same:
    #     level_path = RampLevelPath(from_area = area[0], to_area = area[1])
    #     level_path.save()

    areas = station.children.filter(location_type=5).exists()

    context = {'station':station, 'locations':locations, 'lift_list':lift_list, 'areas': areas}
    return render(request, 'stations/details.html', context)


@login_required
def station_edit(request, id=None, parent=None):
    from .forms import StopForm

    loc_type = int(request.GET.get('loc_type', 1))

    if id:
        station = Stop.objects.get(pk=id)
    elif parent:
        station = Stop(parent_station_id=parent, location_type = loc_type)
    else:
        station = Stop(location_type = loc_type)

    form = StopForm(request.POST or None, request.FILES or None, instance=station)


    if request.method == 'POST':
        if 'delete' in request.POST:
            if station.parent_station:
                parent = station.parent_station
            station.delete()
            if parent:
                return redirect(reverse('station_detail', args=[station.parent_station.pk]))
            else: 
                return redirect(reverse('home'))

        if form.is_valid():
            station = form.save()
            if station.location_type in [0, 1]:
                return redirect(reverse('station_detail', args=[station.pk]))
            elif station.parent_station:
                return redirect(reverse('station_detail', args=[station.parent_station.pk]))
            else:
                return redirect(reverse('home'))
    
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
        lift = Lift()

    form = LiftForm(request.POST or None, request.FILES or None, instance=lift)

    if request.POST:
        if 'delete' in request.POST:
            parent = lift.stop_id.pk
            lift.delete()
            return redirect(reverse('station_detail', args=[parent]))
        if form.is_valid():
            lift = form.save()
            return redirect(reverse('station_detail', kwargs={'id':lift.stop_id_id}))

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
        parent = Stop.objects.get(id = services.platform_id.pk)
        form = ServicesForm(request.POST or None, instance=services)
    
    lines = services.platform_id.parent_station.lines.all()
    for line in lines:
        print(line.stations.all())

    if request.POST:
        if 'delete' in request.POST:
            parent_platform = services.platform_id
            services.delete()
            return redirect(reverse('station_detail', args=[parent_platform.pk]))
        if form.is_valid():
            services = form.save()
            return redirect(reverse('station_detail', args=[services.platform_id.pk]))

    context = {'form': form, 'services': services, 'parent': parent}
    return render(request, 'stations/services/edit.html', context)

import csv
from django.http import HttpResponse

def download_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="stations.csv"'},
    )

    writer = csv.writer(response)
    # fields = Stop._meta.get_fields()
    fields_name = ['name','code' ,'location_type', 'level' ,'parent_station','line', 'platform_code', 'lat', 'lon', 'wheelchair_boarding','visually_impaired_path', 'cardinal_direction','accessible_entrance_id', 'accessible_exit_id','step_free_route_information_available','wifi', 'outside_station_unique_id','blue_badge_car_parking','blue_badge_car_park_spaces', 'taxi_ranks_outside_station','bus_stop_outside_station','train_station' ]

    writer.writerow(fields_name)
    stations = Stop.objects.all().order_by('parent_station')
    for station in stations:
        row = [getattr(station, f, 'null') for f in fields_name]
        writer.writerow(row)

    return response

def lines_index(request):
    lines = Line.objects.all()

        
    context = {'lines': lines}

    return render(request, 'stations/lines/lines.html', context)

def lines_edit(request, id=None):
    from .forms import LineForm

    if id:
        line = Line.objects.get(pk = id)
        print(line)
        form = LineForm(request.POST or None, instance=line)
    else:
        line = None
        form = LineForm(request.POST or None, instance=line)

    if request.POST:
        if 'delete' in request.POST:
            line.delete()
            return redirect(reverse('lines'))
        
        if form.is_valid():
            form.save()
            return redirect(reverse('lines'))
        else:
            return redirect(reverse('home'))

    context= {'form': form}
    return render(request, 'stations/lines/edit.html', context)


def ramps_edit(request, parent=None, id=None):
    from .forms import SameLevelForm
    if parent:
        ramp_parent = Stop.objects.get(pk = parent)
        ramp = RampLevelPath(station = ramp_parent)

    elif id:
        ramp = RampLevelPath.objects.get(pk = id)

    else:
        ramp = None
    
    form = SameLevelForm(request.POST or None, instance= ramp) 

    if request.POST:
        if 'delete' in request.POST:
            ramp.delete()
            return redirect(reverse('station_detail', args=[ramp.station.pk]))
        if form.is_valid():
            ramp = form.save()
            return redirect(reverse('station_detail', args=[ramp.station.pk]))

    context = {'form': form}
    return render(request, 'stations/ramps/edit.html', context)


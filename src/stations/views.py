from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.generic.list import ListView
from .models import *

from django.contrib.auth.decorators import login_required


def choose_city(request):
    from .forms import CityForm
    form = CityForm(request.GET or None)
    if request.GET and form.is_valid():
        city = form.cleaned_data['city']
        return redirect(reverse('stops_list', kwargs={'city': city.slug}))
    context = {'form':form}
    return render(request, 'stations/index.html', context)


def index(request):
    stations = Stop.objects.filter(location_type=Stop.STATION)

    context = {'stations':stations}
    return render(request, 'stations/stations.html', context)


def stations_map(request, city):
    city = City.objects.get(slug=city)

    stations = Stop.objects.filter(location_type=Stop.STATION, city=city)
    markers = [{'lat':s.lat, 'lng':s.lon, 'pk':s.pk, 'name':s.name} for s in stations if s.lat and s.lon]

    lines = Line.objects.all()
    lines = [{'name':l.name, 'color':l.color, 'pk':l.pk, 'path':[{'lat': s.station.lat, 'lng':s.station.lon} for s in l.stations.all()]} for l in lines]
    context = {'stations':stations, 'markers':markers, 'lines':lines, 'city':city}
    return render(request, 'stations/map.html', context)


def station_detail(request, city, id):
    city = City.objects.get(slug=city)

    station = Stop.objects.get(pk=id)
    children = station.children.all()
    lifts = station.lifts.all()

    # copia ascensori
    if request.user.is_superuser and request.method == 'POST' and 'copy' in request.POST:
        lift = Lift.objects.get(pk=request.POST['from'])
        lift.pk = None
        lift.name = f'Copy of {lift.name}'
        lift.stop = station
        lift.save()

    locations = []
    lift_list = []
    if station.location_type == Stop.STATION:
        locations = [
            {'type':type_id, 'name':type_name, 'items':children.filter(location_type=type_id)}
            for type_id, type_name in Stop.LOCATION_TYPES if type_id != station.location_type
        ]
        lift_list = [
            {'type':type_id, 'name':type_name, 'items':lifts.filter(type=type_id), 'others':Lift.objects.filter(type=type_id, stop__city=city)}
            for type_id, type_name in Lift.LIFT_TYPES
        ]
    elif station.location_type == Stop.STOP_PLATFORM:
        locations = [
            {'type':Stop.BOARDING_AREA, 'name':'Boarding area', 'items':children.filter(location_type=Stop.BOARDING_AREA)}
        ]

    areas = station.children.filter(location_type=5).exists()

    context = {'station':station, 'locations':locations, 'lift_list':lift_list, 'areas': areas, 'city':city}
    return render(request, 'stations/details.html', context)


@login_required
def station_edit(request, city, id=None, parent=None):
    from .forms import StopForm

    city = City.objects.get(slug=city)

    loc_type = int(request.GET.get('loc_type', 1))

    if id:
        station = Stop.objects.get(pk=id)
    elif parent:
        station = Stop(parent_station_id=parent, location_type = loc_type, city=city)
    else:
        station = Stop(location_type = loc_type, city=city)

    # campo outside_station_unique_id calcolato
    initial = None
    if station.parent_station and station.location_type in [Stop.STOP_PLATFORM, Stop.ENTRANCE_EXIT]:
        initial = {'outside_station_unique_id':station.parent_station.code + '_OUTSIDE'}

    form = StopForm(request.POST or None, request.FILES or None, instance=station, initial=initial)

    if request.method == 'POST':
        if 'delete' in request.POST:
            if station.parent_station:
                parent = station.parent_station
            station.delete()
            if parent:
                return redirect(reverse('station_detail', args=[city.slug, station.parent_station.pk]))
            else: 
                return redirect(reverse('stops_list', args=[city.slug]))

        if form.is_valid():
            station = form.save(commit=False)
            if not station.city:
                station.city = city
            station.save()
            
            if station.location_type in [0, 1]:
                return redirect(reverse('station_detail', args=[city.slug, station.pk]))
            elif station.parent_station:
                return redirect(reverse('station_detail', args=[city.slug, station.parent_station.pk]))
            else:
                return redirect(reverse('stops_list', args=[city.slug]))
    
    context = {'station':station, 'form':form, 'city':city}
    return render(request, 'stations/edit.html', context)

def lift_detail(request, id):
    lift = Lift.objects.get(pk=id)

    context= {'lift': lift}
    return render(request, 'lifts/details.html', context)

@login_required
def lift_edit(request, city, id=None, parent=None):
    from .forms import LiftForm
    city = City.objects.get(slug=city)

    if id:
        lift = Lift.objects.get(pk=id)
    elif parent:
        lift_type = int(request.GET.get('type'))
        lift = Lift(stop_id=parent, type = lift_type)
    else:
        lift = Lift()

    form = LiftForm(request.POST or None, request.FILES or None, instance=lift)

    if request.POST:
        if 'delete' in request.POST:
            parent = lift.stop.pk
            lift.delete()
            return redirect(reverse('station_detail', args=[city.slug, parent]))
        if form.is_valid():
            lift = form.save()
            return redirect(reverse('station_detail', kwargs={'city':city.slug, 'id':lift.stop_id}))

    context={'form':form, 'lift': lift, 'city':city}
    return render(request, 'lifts/edit.html',context)

@login_required
def services_edit(request, city, platform=None, id=None):
    from .forms import ServicesForm

    city = City.objects.get(slug=city)

    # add
    if platform:
        platform = Stop.objects.get(id = platform)
        service = Services(platform = platform)
    # edit
    elif id:
        service = Services.objects.get(pk = id)
        platform = Stop.objects.get(id = service.platform.pk)
    form = ServicesForm(request.POST or None, instance=service)
    
    if request.POST:
        platform = service.platform
        if 'delete' in request.POST:
            service.delete()
            return redirect(reverse('station_detail', args=[city.slug, platform.pk]))
        if form.is_valid():
            form.save()
            return redirect(reverse('station_detail', args=[city.slug, platform.pk]))

    context = {'form': form, 'services': service, 'platform': platform, 'city':city}
    return render(request, 'stations/services/edit.html', context)

import csv
from django.http import HttpResponse

def download_csv(request, city):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="stations.csv"'},
    )

    writer = csv.writer(response)
    # fields = Stop._meta.get_fields()
    fields_name = ['name','code' ,'location_type', 'level' ,'parent_station','line', 'platform_code', 'lat', 'lon', 'wheelchair_boarding','visually_impaired_path', 'cardinal_direction','accessible_entrance', 'accessible_exit','step_free_route_information_available','wifi', 'outside_station_unique_id','blue_badge_car_parking','blue_badge_car_park_spaces', 'taxi_ranks_outside_station','bus_stop_outside_station','train_station' ]

    writer.writerow(fields_name)
    stations = Stop.objects.filter(city__slug=city).order_by('parent_station')
    for station in stations:
        row = [getattr(station, f, 'null') for f in fields_name]
        writer.writerow(row)

    return response

def lines_index(request, city):
    city = City.objects.get(slug=city)
    lines = Line.objects.filter(city=city)
    context = {'lines': lines, 'city': city}

    return render(request, 'stations/lines/lines.html', context)


@login_required
def line_edit(request, id=None):
    from .forms import LineForm

    line = initial = None
    if id:
        line = Line.objects.get(pk = id)
        initial = {'stations':line.stations.values_list('station', flat=True)}

    form = LineForm(request.POST or None, instance=line, initial=initial)

    if request.method == 'POST':
        if 'delete' in request.POST:
            line.delete()
            return redirect(reverse('lines', args=[city.slug]))
        
        if form.is_valid():
            stations = form.cleaned_data['stations']
            line = form.save()

            # Cancello stazioni già salvate
            LineStation.objects.filter(line=line).delete()

            for i, station in enumerate(stations):
                LineStation.objects.create(line=line, station=station, order=i)
            return redirect(reverse('lines'))

    verbose_name = Line._meta.verbose_name
    context= {'form': form, 'verbose_name':verbose_name}
    return render(request, 'stations/lines/edit.html', context)


@login_required
def ramps_edit(request, city, parent=None, id=None):
    from .forms import SameLevelForm
    city = City.objects.get(slug=city)
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
            return redirect(reverse('station_detail', args=[city.slug, ramp.station.pk]))
        if form.is_valid():
            ramp = form.save()
            return redirect(reverse('station_detail', args=[city.slug, ramp.station.pk]))

    context = {'form': form, 'city':city}
    return render(request, 'stations/ramps/edit.html', context)



def lifts_list(request, city):
    city = City.objects.get(slug=city)
    lifts = Lift.objects.filter(stop__city=city)
    if request.GET.get('type'):
        lifts = lifts.filter(type=request.GET.get('type'))
    context = {'lifts': lifts, 'city': city}
    return render(request, 'lifts/lifts.html', context)

def stops_list(request, city):
    city = City.objects.get(slug=city)
    stops = Stop.objects.filter(city=city).order_by('parent_station', 'name')
    location_type = request.GET.get('type', '1')
    if location_type == '3':
        stops = stops.filter(location_type__in='345')
    else:
        stops = stops.filter(location_type=location_type)
    location_type_name = Stop.LOCATION_TYPES[int(location_type)][1]

    status = request.GET.get('status')
    if status and location_type == '1':
        stops = stops.filter(status=status)

    # Sort stops by parent station name
    stops = list(stops)
    stops.sort(key=lambda x: (x.parent_station and x.parent_station.name or '') + x.name)

    context = {'stops': stops, 'city': city, 'location_type_name': location_type_name}
    return render(request, 'stations/stops.html', context)
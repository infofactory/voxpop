from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.generic.list import ListView
from django.db.models import Q, F
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
    from django.conf import settings
    city = City.objects.get(slug=city)

    stations = Stop.objects.filter(location_type=Stop.STATION, city=city)
    markers = [{'lat':s.lat, 'lng':s.lon, 'pk':s.pk, 'name':s.name} for s in stations if s.lat and s.lon]

    lines = Line.objects.all()
    lines = [{'name':l.name, 'color':l.color, 'pk':l.pk, 'path':[{'lat': s.station.lat, 'lng':s.station.lon} for s in l.stations.all()]} for l in lines]
    context = {'stations':stations, 'markers':markers, 'lines':lines, 'city':city, 'api_key': settings.GOOGLE_MAPS_API_KEY}
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

def lift_detail(request, city, id):
    from .forms import LiftForm

    lift = Lift.objects.get(pk=id)
    city = City.objects.get(slug=city)
    form = LiftForm(instance=lift)

    context= {'lift': lift, 'city': city, 'form':form}
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

    # Caricamento stato ascensore da I am a willer
    if lift.pk:
            
        ultima_segnalazione = lift.segnalazioni.order_by('-created').first()
        if ultima_segnalazione:
            lift.status = ultima_segnalazione.working


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


def lift_thumbnail(request, id):
    from django.shortcuts import get_object_or_404
    lift = get_object_or_404(Lift, pk=id)
    return redirect(lift.get_thumbnail())


def download_gtfs(request, city_slug, filename=None):
    import csv
    import zipfile
    from django.http import HttpResponse, HttpResponseNotFound

    city = City.objects.get(slug=city_slug)
    if not filename:
        response = HttpResponse(
            content_type='application/zip',
            headers={'Content-Disposition': 'attachment; filename="%s-gtfs.zip"' % city_slug},
        )
    
    elif filename.endswith('.txt'):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="%s"' % filename},
        )

    else:
        return HttpResponseNotFound()
    
    if filename == 'feed_info.txt':
        keys = ['feed_publisher_name', 'feed_publisher_url', 'feed_lang', 'feed_start_date']
        publisher = {
            'feed_publisher_name': 'Willeasy srl',
            'feed_publisher_url': 'https://www.willeasy.net',
            'feed_lang': 'en',
            'feed_start_date': '20230601',
            'feed_end_date': '20231231',
            'feed_version': '1.0',
            'feed_contact_email': 'info@willeasy.net',
        }
        writer = csv.writer(response)
        writer.writerow(keys)
        writer.writerow([publisher[k] for k in keys])
    
    if filename == 'levels.txt':
        keys = ['level_id', 'level_index', 'level_name']
        writer = csv.writer(response)
        writer.writerow(keys)
        for level in range(-4, 2):
            writer.writerow([level, level, ''])

    
    if filename == 'stops.txt':
        keys = ['stop_id', 'stop_code', 'stop_name', 'stop_desc', 'stop_lat', 'stop_lon', 'location_type', 'parent_station', 'wheelchair_boarding', 'level_id', 'platform_code']
        writer = csv.writer(response)
        writer.writerow(keys)

        mandatory_position = Q(location_type__in = [Stop.STOP_PLATFORM, Stop.STATION, Stop.ENTRANCE_EXIT])
        for stop in Stop.objects.filter(mandatory_position & Q(lat__isnull=False) & Q(lon__isnull=False) | ~mandatory_position, city=city).exclude(code=''):
            writer.writerow([
                stop.code,
                stop.code,
                stop.name.title(),
                stop.desc,
                stop.lat,
                stop.lon,
                stop.location_type == 5 and 3 or stop.location_type,
                stop.parent_station and stop.parent_station.code or '',
                stop.wheelchair_boarding,
                stop.level,
                stop.platform_code,
            ])
    
    if filename == 'pathways.txt':
        keys = ['pathway_id', 'from_stop_id', 'to_stop_id', 'pathway_mode', 'is_bidirectional', 'stair_count', 'max_slope', 'min_width', 'signposted_as', 'reversed_signposted_as']
        writer = csv.writer(response)
        writer.writerow(keys)
        for lift in Lift.objects.filter(stop__city=city, from_area__isnull=False, to_area__isnull=False).exclude(from_area__code=F('to_area__code')).exclude(type=Lift.STAIRLIFT):
            notes = lift.notes.replace('\r', ' ').replace('\n', ' ') or ''
            if notes == notes.upper():
                notes = notes.capitalize()
            writer.writerow([
                lift.name,
                lift.from_area.code,
                lift.to_area.code,
                2 if lift.type == Lift.STAIR else 5 if lift.type == Lift.LIFT else 4 if lift.type == Lift.ESCALATOR and lift.pathway_mode == 4 else 3 if lift.type == Lift.ESCALATOR and lift.pathway_mode == 3 else '',
                1 if lift.type in [Lift.STAIR, Lift.LIFT] else 0,
                lift.number_of_steps or '',
                '',
                '',
                notes,
                '',
            ])

    if not filename:
        filenames = ['stops.txt', 'feed_info.txt', 'levels.txt', 'pathways.txt']
        with zipfile.ZipFile(response, 'w') as zip_file:
            for filename in filenames:
                r = download_gtfs(request, city_slug, filename)
                zip_file.writestr(filename, r.getvalue())

    return response



def download_custom(request, city_slug, filename=None):
    import csv
    import zipfile
    from django.http import HttpResponse, HttpResponseNotFound

    city = City.objects.get(slug=city_slug)
    if not filename:
        response = HttpResponse(
            content_type='application/zip',
            headers={'Content-Disposition': 'attachment; filename="%s-data.zip"' % city_slug},
        )
    
    elif filename.endswith('.csv'):
        response = HttpResponse(
            content_type='text/plain',
          #  headers={'Content-Disposition': 'attachment; filename="%s"' % filename},
        )

    else:
        return HttpResponseNotFound()
    
    if filename == 'FeedInfo.csv':

        keys = ['FeedPublisherName', 'FeedPublisherUrl', 'FeedLang', 'FeedStartDate']
  
        publisher = {
            'FeedPublisherName': 'Willeasy srl',
            'FeedPublisherUrl': 'https://www.willeasy.net',
            'FeedLang': 'en',
            'FeedStartDate': '2023-06-01T08:00+00:00',

        }
        writer = csv.writer(response)
        writer.writerow(keys)
        writer.writerow([publisher[k] for k in keys])
    
    if filename == 'PlatformServices.csv':
        keys = ['PlatformUniqueId', 'Line', 'DirectionTowards', 'MinGap', 'MaxGap', 'AverageGap', 'MinStep', 'MaxStep', 'AverageStep', 'DesignatedLevelAccessPoint', 'LocationOfLevelAccess', 'LevelAccessByManualRamp', 'AdditionalAccessibilityInformation']
        writer = csv.writer(response)
        writer.writerow(keys)

        for service in Services.objects.filter(platform__city=city):
            writer.writerow([
                service.platform.code,
                service.line,
                service.direction_towards,
                service.min_gap,
                service.max_gap,
                service.average_gap,
                service.min_step,
                service.max_step,
                service.average_step,
                int(service.designated_level_access_point),
                service.location_of_level_access and service.location_of_level_access.name or '',
                int(service.level_access_by_manual_ramp),
                service.additional_accessibility_info,
            ])
    
    if filename == 'Platforms.csv':

        keys = ['UniqueId','StationUniqueId','PlatformNumber','CardinalDirection','FriendlyName','AccessibleEntranceName','HasStepFreeRouteInformation']
        writer = csv.writer(response)
        writer.writerow(keys)

        for stop in Stop.objects.filter(location_type = Stop.STOP_PLATFORM, city=city):
            writer.writerow([
                stop.code,
                stop.parent_station.code,
                stop.platform_code,
                stop.cardinal_direction,
                stop.name,
                stop.accessible_entrance and stop.accessible_entrance.name or '',
                int(stop.step_free_route_information_available),
            ])
    
    if filename == 'Lifts.csv':
        keys = ['StationUniqueId', 'DeviceUniqueId', 'DeviceId', 'DeviceType', 'DeviceName', 'FriendlyName', 'FromAreas', 'IntermediateAreas', 'IntermediateAreas2', 'ToAreas', 'LimitedCapacityDevice', 'DeviceNotes']
        writer = csv.writer(response)
        writer.writerow(keys)
        for lift in Lift.objects.filter(stop__city=city):
            notes = lift.notes.replace('\r', ' ').replace('\n', ' ') or ''
            if notes == notes.upper():
                notes = notes.capitalize()
            writer.writerow([
                lift.stop.code,
                lift.name,
                lift.name,
                lift.type,
                lift.name,
                lift.friendly_name,
                lift.from_area.code if lift.from_area else '',
                lift.intermediate_area1.code if lift.intermediate_area1 else '',
                lift.intermediate_area2.code if lift.intermediate_area2 else '',
                lift.to_area.code if lift.to_area else '',
                '',
                notes,
            ])

    if filename == 'RampRoutes.csv':

        keys = ['From', 'To']
        writer = csv.writer(response)
        writer.writerow(keys)

    if filename == 'SameLevelPaths.csv':

        keys = ['From', 'To']
        writer = csv.writer(response)
        writer.writerow(keys)

        for ramp in RampRoutes.objects.filter(station__city=city):
            writer.writerow([
                ramp.from_area.code,
                ramp.to_area.code,
            ])

    if filename == 'StationPoints.csv':
        keys = ['UniqueId','StationUniqueId','AreaName','AreaId','Level','Lat','Lon','FriendlyName']
        writer = csv.writer(response)
        writer.writerow(keys)

        for area in Stop.objects.filter(city=city, location_type__in=[Stop.AREA, Stop.BOARDING_AREA]):
            writer.writerow([
                area.code,
                area.parent_station.code,
                area.name,
                area.code,
                area.level,
                area.lat,
                area.lon,
                area.name,
            ])

    if filename == 'Stations.csv':
        keys = ['UniqueId','Name','Wifi','OutsideStationUniqueId','BlueBadgeCarParking','BlueBadgeCarParkSpaces','TaxiRanksOutsideStation','MainBusInterchange','PierInterchange','NationalRailInterchange','AirportInterchange']
        writer = csv.writer(response)
        writer.writerow(keys)

        for station in Stop.objects.filter(city=city, location_type=Stop.STATION):
            writer.writerow([
                station.code,
                station.name,
                int(station.wifi),
                station.outside_station_unique_id,
                int(station.blue_badge_car_parking),
                station.blue_badge_car_park_spaces,
                int(station.taxi_ranks_outside_station),
                int(station.bus_stop_outside_station),
                0, # pier
                int(station.train_station),
                0, #airport
            ])



    if filename == 'StepFreeInterchangeInfo.csv':
        
        keys = ['FromPlatformUniqueId','ToPlatformUniqueId','DistanceInMetres']
        writer = csv.writer(response)
        writer.writerow(keys)

        for info in StepFreeInterchangeInfo.objects.filter(station__city=city):
            writer.writerow([
                info.from_area and info.from_area.code or '',
                info.to_area and info.to_area.code or '',
                info.distance,
            ])




    if not filename:
        filenames = ['FeedInfo.csv', 'PlatformServices.csv', 'Platforms.csv', 'Lifts.csv', 'RampRoutes.csv', 'SameLevelPaths.csv', 'StationPoints.csv', 'Stations.csv', 'StepFreeInterchangeInfo.csv']
        with zipfile.ZipFile(response, 'w') as zip_file:
            for filename in filenames:
                r = download_custom(request, city_slug, filename)
                zip_file.writestr(filename, r.getvalue())

    return response


def download_realtime(request, city_slug):
    segnalazioni = Segnalazione.objects.filter(lift__stop__city__slug=city_slug, working=False)
    context = {
        'segnalazioni': segnalazioni,
    }
    return render(request, 'download_realtime.html', context, content_type='text/plain; charset=utf-8')

from django.core.management.base import BaseCommand

from stations.models import *
import csv
from django.template.defaultfilters import slugify

FILENAME = 'stops.csv'
 
class Command(BaseCommand):
    help = 'Carica le fermate'

    def handle(self, *args, **options):
        with open(FILENAME) as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                stop_id, stop_name, stop_code, visible, fare_zone_id, stop_lon, stop_lat, location_type, parent_station, stop_timezone, geometry_id, equipment_id, level_id, platform_code, address_id = row
                if location_type == '1':
                    station = Stop.objects.filter(location_type=1, code=stop_id).first() or Stop(location_type=1, code=stop_id)
                    station.location_type = 1
                    station.lat = stop_lat
                    station.lon = stop_lon
                    station.name = stop_name
                    print(station.location_type, station)
                    station.save()

        with open(FILENAME) as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                stop_id, stop_name, stop_code, visible, fare_zone_id, stop_lon, stop_lat, location_type, parent_station, stop_timezone, geometry_id, equipment_id, level_id, platform_code, address_id = row
                if location_type == '0':
                    station = Stop.objects.filter(location_type=0, code=stop_id).first() or Stop(location_type=0, code=stop_id)
                    station.location_type = 0
                    station.lat = stop_lat
                    station.lon = stop_lon
                    station.name = stop_name

                    parent = Stop.objects.filter(code=parent_station).first()
                    station.parent_station = parent
                    print(station.location_type, station)
                    station.save()
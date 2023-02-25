from django.core.management.base import BaseCommand

from stations.models import *
import csv
from django.template.defaultfilters import slugify

FILENAME = 'lines.csv'
 
class Command(BaseCommand):
    help = 'Aggiusta le linee'

    def handle(self, *args, **options):
        with open(FILENAME) as csvfile:
            for elem in LineStation.objects.all():
                if elem.station.parent_station:
                    elem.station = elem.station.parent_station
                    elem.save()
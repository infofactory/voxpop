from django.core.management.base import BaseCommand

from stations.models import *
import csv
from django.template.defaultfilters import slugify

FILENAME = 'lines.csv'
 
class Command(BaseCommand):
    help = 'Carica le linee'

    def handle(self, *args, **options):
        with open(FILENAME) as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            LineStation.objects.all().delete()
            for row in reader:
                print(row)
                stop_id, line_id, order = row[:3]
                line = Line.objects.filter(code=line_id).first()
                station = Stop.objects.filter(code=stop_id).first()
                if line and station:
                    LineStation.objects.get_or_create(line=line, station=station, defaults={'order':order})
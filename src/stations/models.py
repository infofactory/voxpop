from django.db import models
from django.urls import reverse



class Stop(models.Model):

    STOP_PLATFORM = 0
    STATION = 1
    ENTRANCE_EXIT = 2
    GENERIC_NODE = 3
    BOARDING_AREA = 4
    AREA = 5

    LOCATION_TYPES = (
        (STOP_PLATFORM, "Stop or platform"),
        (STATION, "Station"),
        (ENTRANCE_EXIT, "Entrance/Exit"),
        (GENERIC_NODE, "Generic node"),
        (BOARDING_AREA, "Boarding area"),
        (AREA, "Area"),
    )

    CARDINAL_DIRECTIONS = (
        ("N", "North"),
        ("E", "East"),
        ("W", "West"),
        ("S", "South"),
    )

    WHEELCHAIR_BOARDING = (
        (0,"No info"),
        (1,"Yes, there is"),
        (2,"No"),
    )

    VISUALLY_IMPAIRED_PATH = (
        (0,'No info for the stop'),
        (1, 'Yes'),
        (2, 'No'),
        (3, 'Only in some areas')
    )

    code = models.CharField(verbose_name='Stop ID', max_length=20, blank=True)
    name = models.CharField(max_length=100)
    lines = models.ManyToManyField('stations.Line', related_name='stations', blank=True)
    desc = models.TextField(verbose_name="Description", blank=True, null=True)
    lat = models.FloatField(verbose_name="Latitude", blank=True, null=True)
    lon = models.FloatField(verbose_name="Longitude", blank=True, null=True)
    location_type = models.IntegerField(choices=LOCATION_TYPES, default=1)
    level = models.IntegerField(blank=True, null=True)
    parent_station = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    wheelchair_boarding = models.IntegerField(choices=WHEELCHAIR_BOARDING, default=0)
    visually_impaired_path = models.IntegerField(choices=VISUALLY_IMPAIRED_PATH, default=0)
    platform_code = models.CharField(max_length=20, blank=True)
    cardinal_direction = models.CharField(max_length=1, blank=True, choices=CARDINAL_DIRECTIONS )
    accessible_entrance = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="+")
    accessible_exit = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="+")
    step_free_route_information_available = models.BooleanField(default=False)
    wifi = models.BooleanField(default=False)
    outside_station_unique_id = models.CharField(max_length=50, blank=True)
    blue_badge_car_parking = models.BooleanField(default=False)
    blue_badge_car_park_spaces = models.BooleanField(default=False)
    taxi_ranks_outside_station = models.BooleanField(default=False)
    bus_stop_outside_station = models.BooleanField(default=False)
    train_station = models.BooleanField(default=False)
    image = models.ImageField(blank=True, upload_to='stops')

    def __str__(self) -> str:
        return self.name

    @property
    def ancestors(self):
        ancestors = []
        current = self
        while current.parent_station:
            ancestors.append(current.parent_station)
            current = current.parent_station
        return ancestors

    @property
    def url(self):
        if self.pk:
            return reverse('station_detail', args=[self.pk])
        else:
            return reverse('home')
    class Meta:
        ordering=('name',)
    



class Lift(models.Model):
    HANDRAIL = (
        (0, 'no'),
        (1, 'right'),
        (2, 'left'),
        (3, 'both'),
    )

    STEPS = ((0, 'No'), (1, 'tapis roulant'))

    LIFT = 0
    STAIRLIFT = 1
    STAIR = 2
    ESCALATOR = 3

    LIFT_TYPES = (
        (LIFT, 'Lift'),
        (STAIRLIFT, 'Stairlift'),
        (STAIR, 'Stair'),
        (ESCALATOR, 'Escalator'),
    )

    type = models.IntegerField(choices=LIFT_TYPES)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name="lifts")
    name = models.CharField(max_length=100)
    friendly_name = models.CharField(max_length=100, blank=True, null=True)
    from_area = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='+')
    intermediate_area1 = models.ForeignKey(Stop, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    intermediate_area2 = models.ForeignKey(Stop, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    to_area = models.ForeignKey(Stop, on_delete=models.CASCADE)
    lift_width = models.PositiveIntegerField(blank=True, null=True, help_text='width in millimeters')    #solo per lift
    lift_height = models.PositiveIntegerField(blank=True, null=True, help_text='height in millimeters')   #solo per lift
    visually_impaired_ok = models.BooleanField(default=False)
    assistance_required = models.BooleanField(default=False) #solo per stair 
    number_of_steps = models.PositiveIntegerField(default=0)    #solo per stair
    steps_height = models.FloatField(default=0, help_text='height in centimeters')                          #solo per stair
    handrail = models.IntegerField(choices=HANDRAIL, default=0) #solo per stair
    handrail_height = models.FloatField(default=False, help_text='height in centimeters')                       #solo per stair
    steps = models.IntegerField(choices=STEPS, default=0)       #solo per strair e escalator
    notes = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, upload_to='lifts')

    def __str__(self) -> str:
        return  self.name

        

class RampRoutes(models.Model):
    station = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='ramps')
    from_area = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='ramp_routes')
    to_area = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='+')

class RampLevelPath(RampRoutes):
    pass

class StepFreeInterchangeInfo(RampRoutes):
    distance = models.IntegerField(blank=True, null=True)

class Services(models.Model):
    platform = models.OneToOneField('stations.Stop', on_delete=models.CASCADE, primary_key=True)
    line = models.ForeignKey('stations.Line', on_delete=models.CASCADE, blank=True, null=True, related_name='platforms')
    direction_towards = models.ForeignKey(Stop, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    min_gap = models.IntegerField(null=True, blank=True)
    max_gap = models.IntegerField(null=True, blank=True)
    avarage_gap = models.IntegerField(null=True, blank=True)
    min_step = models.IntegerField(null=True, blank=True)
    max_step = models.IntegerField(null=True, blank=True)
    avarage_step = models.IntegerField(null=True, blank=True)
    designated_level_acces_point = models.BooleanField(default=False)
    location_of_level_access = models.ForeignKey('stations.Stop', on_delete=models.CASCADE, related_name='+', null=True, blank=True)
    level_access_by_manual_ramp = models.BooleanField(default=False)
    additional_accessibility_info = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return "%s services" % self.platform

class Line(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, blank=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        ordering = ('name',)
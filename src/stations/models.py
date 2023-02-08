from django.db import models
from django.urls import reverse


class Stop(models.Model):
    LOCATION_TYPES = (
        (0, "Stop or platform"),
        (1, "Station"),
        (2, "Entrance/Exit"),
        (3, "Generic node"),
        (4, "Boarding area"),
        (5, "Area"),
    )

    CARDINAL_DIRECTIONS = (
        ("N", "Nord"),
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

    code = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=100)
    desc = models.TextField(verbose_name="Description", blank=True, null=True)
    lat = models.FloatField(verbose_name="Latitude", blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    location_type = models.IntegerField(choices=LOCATION_TYPES, default=1)
    level = models.IntegerField(blank=True, null=True)
    parent_station = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    wheelchair_boarding = models.IntegerField(choices=WHEELCHAIR_BOARDING, default=0)
    visually_impaired_path = models.IntegerField(choices=VISUALLY_IMPAIRED_PATH, default=0)
    platform_code = models.CharField(max_length=20, blank=True, null=True)
    cardinal_direction = models.CharField(max_length=1, blank=True, null=True, choices=CARDINAL_DIRECTIONS )
    accessible_entrance_id = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="+")
    accessible_exit_id = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="+")
    step_free_route_information_available = models.BooleanField(default=False)
    wifi = models.BooleanField(default=False)
    outside_station_unique_id = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    blue_badge_car_parking = models.BooleanField(default=False)
    blue_badge_car_park_spaces = models.BooleanField(default=False)
    taxi_ranks_outside_station = models.BooleanField(default=False)
    bus_stop_outside_station = models.BooleanField(default=False)
    train_station = models.BooleanField(default=False)

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

    LIFT_TYPES = (
        (0, 'Lift'),
        (1, 'Stairlift'),
        (2, 'Stair'),
        (3, 'Escalator'),
    )

    type = models.IntegerField(choices=LIFT_TYPES)
    stop_id = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name="lifts")
    name = models.CharField(max_length=100)
    friendly_name = models.CharField(max_length=100, blank=True, null=True)
    from_areas = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='+')
    intermediate_areas = models.ForeignKey(Stop, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    intermediate_areas_two = models.ForeignKey(Stop, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    to_areas = models.ForeignKey(Stop, on_delete=models.CASCADE)
    lift_width = models.FloatField(blank=True, null=True, help_text='width in centimeters')    #solo per lift
    lift_heigth = models.FloatField(blank=True, null=True, help_text='height in centimeters')   #solo per lift
    visually_impaired_ok = models.BooleanField(default=False)
    assistance_requested = models.BooleanField(default=False) #solo per strair 
    number_of_steps = models.PositiveIntegerField(default=0)    #solo per stair
    steps_height = models.FloatField(default=0, help_text='height in centimeters')                          #solo per stair
    handrail = models.IntegerField(choices=HANDRAIL, default=0) #solo per stair
    handrail_height = models.FloatField(default=False, help_text='height in centimeters')                       #solo per stair
    steps = models.IntegerField(choices=STEPS, default=0)       #solo per strair e escalator
    lift_notes = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return  self.name

        

# class Stairlift(models.Model):
#     stop_id = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='Stairlifts')
#     name = models.CharField(max_length=100)
#     friendly_name = models.CharField(max_length=100, blank=True, null=True)
#     from_areas = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='+')
#     to_areas = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='+')
#     assistance_requested = models.BooleanField(default=False)

#     def __str__(self) -> str:
#         return self.name

# class Stair(Stairlift):
#     HANDRAIL = (
#         (0, 'no'),
#         (1, 'right'),
#         (2, 'left'),
#         (3, 'both'),
#     )

#     number_of_steps = models.PositiveIntegerField(default=1)
#     steps_height = models.FloatField()
#     handrail = models.IntegerField(choices=HANDRAIL, default=0)
#     handrail_height = models.FloatField()

# class Escalator(Stairlift):
    # STEPS = ((0, 'No'), (1, 'tapis roulant'))

    # steps = models.IntegerField(choices=STEPS, default=0)

class RampRoutes(models.Model):
    from_area = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='ramp_routes')
    to_area = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='+')

class RampLevelPath(RampRoutes):
    pass

class StepFreeInterchangeInfo(RampRoutes):
    distance = models.IntegerField(blank=True, null=True)

class Services(models.Model):
    platform_id = models.OneToOneField('stations.Stop', on_delete=models.CASCADE, primary_key=True)
    # line = models.ForeignKey(RampRoutes, on_delete=models.CASCADE, related_name='lines')
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
        name = "%s %s" % (self.platform_id, 'services')
        return name


    
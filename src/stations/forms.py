from django.forms import ModelForm
from django import forms
from .models import *

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field,MultiField, Submit, Row, Column, HTML
from crispy_forms.bootstrap import StrictButton
from django.forms.widgets import HiddenInput


class StopForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # location_types:
        # 0=stop/platform
        # 1=station
        # 2=entrace/exit
        # 3=generic mode
        # 4=boarding area
        # 5=area
        if self.instance.location_type != 1:
            del self.fields['lines']

        if self.instance.location_type == 0:
            self.fields['platform_code'].required = True
            self.fields['cardinal_direction'].required = True
            doors = Stop.objects.filter(
                location_type=2, parent_station=self.instance.parent_station)

            self.fields['accessible_entrance_id'].queryset = doors
            self.fields['accessible_exit_id'].queryset = doors

        if self.instance.location_type != 0:
            del self.fields['accessible_entrance_id']
            del self.fields['accessible_exit_id']
            # del self.fields['step_free_route_information_available']
        if self.instance.location_type in [0, 1, 2]:
            self.fields['lat'].required = True
            self.fields['lon'].required = True
        if self.instance.location_type == 2:
            del self.fields['wifi']
        if self.instance.location_type not in [0, 2]:
            del self.fields['outside_station_unique_id']

        self.helper = FormHelper()
        self.helper.layout = Layout( 
            Row(
                Column('code', css_class='col-sm-1 col-3'),
                Column('name', css_class='col-sm-11 col-6')
            ),
            Field('lines', css_class='form-select'),
            Row(
                'level'
            ),
            Row(
                Column('desc', css_class='col-12')
            ),
            Row(
                Column('lat', css_class='col-5'),
                Column('lon', css_class='col-5'),
                HTML('<div class="wrapper-btn col-2" ><button type="button" class="btn btn-primary" id="auto-locate"><i class="fa-solid fa-map-pin"></i></button></div>'),
            ),
            Row(
                Column('wheelchair_boarding',
                       css_class='col-sm-4 col-md-3 col-lg-2 col-12'),
                Column('visually_impaired_path',
                       css_class='col-sm-4 col-md-3 col-lg-2 col-12'),

                Column('platform_code',
                       css_class='col-sm-4 col-md-3 col-lg-2 col-12'),
                Column('cardinal_direction',
                       css_class='col-sm-4 col-md-3 col-lg-2 col-12'),

                Column('accessible_entrance_id',
                       css_class='col-sm-4 col-md-3 col-lg-2 col-12'),
                Column('accessible_exit_id',
                       css_class='col-sm-4 col-md-3 col-lg-2 col-12'),
            ),
            Row(
                Column('outside_station_unique_id')
            ),
            Field('wifi', css_class="form-check-input",
                  wrapper_class="form-check form-switch"),
            Field('step_free_route_information_available',
                  css_class="form-check-input", wrapper_class="form-check form-switch"),
            Field('blue_badge_car_parking', css_class="form-check-input",
                  wrapper_class="form-check form-switch"),
            Field('blue_badge_car_park_spaces', css_class="form-check-input",
                  wrapper_class="form-check form-switch"),
            Field('taxi_ranks_outside_station', css_class="form-check-input",
                  wrapper_class="form-check form-switch"),
            Field('bus_stop_outside_station', css_class="form-check-input",
                  wrapper_class="form-check form-switch"),
            Field('train_station', css_class="form-check-input",
                  wrapper_class="form-check form-switch"),
            StrictButton('<i class="fas fa-paper-plane"></i> Save',
                         type="submit", name="save", css_class='btn btn-success me-4'),
            StrictButton('<i class="fas fa-trash"></i> Delete',
                         type="submit", name="delete", css_class='btn btn-danger'),
        )

    class Meta:
        model = Stop
        exclude = ['parent_station', 'location_type']
        widgets = {
            'desc': forms.Textarea(attrs={
                'rows': 2
            })
        }


class LiftForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('save', 'Save', css_class='btn btn-success me-4'))
        self.helper.add_input(
            Submit('delete', 'Delete', css_class='btn btn-danger'))

        areas = Stop.objects.filter(
            location_type=5, parent_station=self.instance.stop_id.pk)
        if areas:
            self.fields['from_areas'].queryset = areas
            self.fields['intermediate_areas'].queryset = areas
            self.fields['intermediate_areas_two'].queryset = areas
            self.fields['to_areas'].queryset = areas

        if self.instance.type == 0:
            self.fields['lift_width'].required = True
            self.fields['lift_heigth'].required = True
        else:
            del self.fields['lift_width']
            del self.fields['lift_heigth']

        if self.instance.type != 2:
            del self.fields['number_of_steps']
            del self.fields['steps_height']
            del self.fields['handrail']
            del self.fields['handrail_height']

        if self.instance.type != 3:
            del self.fields['steps']

    class Meta:
        model = Lift
        exclude = ['stop_id', 'type']


class ServicesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('save', 'Save', css_class='btn btn-success me-4'))
        self.helper.add_input(
            Submit('delete', 'Delete', css_class='btn btn-danger'))

        locations = Stop.objects.filter(location_type = 4, parent_station = self.instance.platform_id.pk)
        self.fields['location_of_level_access'].queryset = locations

        self.helper.layout = Layout(
            Row(
                Column('min_gap', css_class='col-6 col-sm-4 flex-grow-1'),
                Column('max_gap', css_class='col-6 col-sm-4 flex-grow-1'), 
                Column('avarage_gap', css_class='col-6 col-sm-4 flex-grow-1')
            ),
            Row(
                Column('min_step', css_class='col-6 col-sm-4 flex-grow-1'), 
                Column('max_step', css_class='col-6 col-sm-4 flex-grow-1'), 
                Column('avarage_step', css_class='col-6 col-sm-4 flex-grow-1')
            ),
            Row(
                Column('designated_level_acces_point', css_class='form-check form-switch'),
                Column('level_access_by_manual_ramp', css_class='form-check form-switch'),
            ),
            Row('location_of_level_access'),
            Row('additional_accessibility_info')
        )
    class Meta:
        model = Services
        exclude = ['platform_id']
        widgets = {
            'additional_accessibility_info': forms.Textarea(attrs={
                'rows': 2
            })
        }

class LineForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('save', 'Save', css_class='btn btn-success me-4'))
        self.helper.add_input(
            Submit('delete', 'Delete', css_class='btn btn-danger'))
        
        self.helper.layout = Layout(
            Row(
                Column('name', 'color')
            ),
            HTML(
            '<div class="d-flex align-items-center "><label for="color_pick ">Pick a color</label><div class="" id="defaults"></div></div>'
            )
        )

    class Meta:
        model = Line
        fields = '__all__'

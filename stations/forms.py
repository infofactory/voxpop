from django.forms import ModelForm
from django import forms
from .models import *

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field,MultiField, Submit, Row, Column, HTML
from crispy_forms.bootstrap import StrictButton
from django.forms.widgets import HiddenInput


class CityForm(forms.Form):
    city = forms.ModelChoiceField(queryset=City.objects.all(), label="Choose your city", empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.add_input(
            Submit('go', 'Go', css_class='btn btn-success me-4'))

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

        if self.instance.location_type != Stop.STATION:
            del self.fields['status']


        if self.instance.location_type == Stop.STOP_PLATFORM:
            self.fields['platform_code'].required = True
          #  self.fields['cardinal_direction'].required = True
            doors = Stop.objects.filter(location_type=Stop.ENTRANCE_EXIT, parent_station=self.instance.parent_station)

            self.fields['accessible_entrance'].queryset = doors
            self.fields['accessible_exit'].queryset = doors

        if self.instance.location_type != Stop.STOP_PLATFORM:
            del self.fields['accessible_entrance']
            del self.fields['accessible_exit']
            del self.fields['platform_code']
            del self.fields['cardinal_direction']
        # if self.instance.location_type != Stop.GENERIC_NODE:
        #     self.fields['lat'].required = True
        #     self.fields['lon'].required = True
        if self.instance.location_type == Stop.ENTRANCE_EXIT:
            del self.fields['wifi']

        if self.instance.location_type not in [Stop.STOP_PLATFORM, Stop.ENTRANCE_EXIT]:
            del self.fields['outside_station_unique_id']
      

        if self.instance.location_type == Stop.ENTRANCE_EXIT:
            self.fields['wheelchair_boarding'].choices = (
                (0, "Inherit from {}".format(self.instance.parent_station)),
                (1, "Station entrance is wheelchair accessible"),
                (2, "No accessible path from station entrance to stops/platforms"),
            )
        elif self.instance.parent_station:
            self.fields['wheelchair_boarding'].choices = (
                (0, "Inherit from {}".format(self.instance.parent_station)),
                (1, "There exists some accessible path from outside the station to the specific stop/platform"),
                (2, "There exists no accessible path from outside the station to the specific stop/platform"),
            )
        else:
            self.fields['wheelchair_boarding'].choices = (
                (0, "No accessibility information for the stop"),
                (1, "Some vehicles at this stop can be boarded by a rider in a wheelchair"),
                (2, "Wheelchair boarding is not possible at this stop"),
            )
            

        self.helper = FormHelper()
        self.helper.layout = Layout( 
            Row(
                Column('code', css_class='col-sm-2 col-3'),
                Column('name', css_class='col-sm-10 col-6')
            ),
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
                       css_class='col-sm-6 col-12'),
                Column('visually_impaired_path',
                       css_class='col-sm-6 col-12'),
            ),
            Row(
                Column('platform_code',
                       css_class='col-sm-4 col-md-3 col-12'),
                Column('cardinal_direction',
                       css_class='col-sm-4 col-md-3 col-12'),

                Column('accessible_entrance',
                       css_class='col-sm-4 col-md-3 col-12'),
                Column('accessible_exit',
                       css_class='col-sm-4 col-md-3 col-12'),
            ),
            Row(
                Column('outside_station_unique_id'),
            ),
            Row(
                Column('image'),
            ),
            Field('wifi', css_class="form-check-input",
                  wrapper_class="form-check form-switch"),
            Field('step_free_route_information_available',
                  css_class="form-check-input", wrapper_class="form-check form-switch"),
            Field('blue_badge_car_parking', css_class="form-check-input",
                  wrapper_class="form-check form-switch"),
            Field('blue_badge_car_park_spaces'),
            Field('taxi_ranks_outside_station', css_class="form-check-input",
                  wrapper_class="form-check form-switch"),
            Field('bus_stop_outside_station', css_class="form-check-input",
                  wrapper_class="form-check form-switch"),
            Field('train_station', css_class="form-check-input",
                  wrapper_class="form-check form-switch"),

            Row(
                Column('status', css_class='col-12'),
            ),

            StrictButton('<i class="fas fa-paper-plane"></i> Save',
                         type="submit", name="save", css_class='btn btn-success me-4'),
            )

        if self.instance.pk:
            self.helper.layout.append(
                StrictButton('<i class="fas fa-trash"></i> Delete', type="submit", name="delete", css_class='btn btn-danger'))
        
    class Meta:
        model = Stop
        exclude = ['parent_station', 'location_type']
        widgets = {
            'desc': forms.Textarea(attrs={
                'rows': 2
            }),
            'wheelchair_boarding': forms.RadioSelect,
        }


class LiftForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout( 
            Row(
                Column('name', css_class='col-md-6'),
                Column('friendly_name', css_class='col-md-6'),
            ),
            Row(
                Column('from_area', css_class='col-md-6'),
                Column('to_area', css_class='col-md-6'),
            ),
            Row(
                Column('intermediate_area1', css_class='col-md-6'),
                Column('intermediate_area2', css_class='col-md-6'),
            ),
            Row(
                Column('lift_width', css_class='col-md-6'),
                Column('lift_depth', css_class='col-md-6'),
            ),
            Row(
                Column('visually_impaired_ok', css_class='col-md-6'),
                Column('assistance_required', css_class='col-md-6'),
            ),
            Row(
                Column('number_of_steps', css_class='col-md-4'),
                Column('steps_height', css_class='col-md-4'),
                Column('pathway_mode', css_class='col-md-4'),
            ),
            Row(
                Column('handrail', css_class='col-md-6'),
                Column('handrail_height', css_class='col-md-6'),
            ),
            Row(
                Column('notes', css_class='col-12'),
                Column('image', css_class='col-12'),
                Column('status', css_class='col-12'),
            ),
                    
        )

        self.helper.add_input(
            Submit('save', 'Save', css_class='btn btn-success me-4'))
        if self.instance.pk:
            self.helper.add_input(
                Submit('delete', 'Delete', css_class='btn btn-danger'))

        areas = Stop.objects.filter(
            location_type__in=[Stop.AREA, Stop.ENTRANCE_EXIT, Stop.GENERIC_NODE], parent_station=self.instance.stop.pk)
        if areas:
            self.fields['from_area'].queryset = areas
            self.fields['intermediate_area1'].queryset = areas
            self.fields['intermediate_area2'].queryset = areas
            self.fields['to_area'].queryset = areas
        else:
            del self.fields['intermediate_area1']
            del self.fields['intermediate_area2']
            del self.fields['to_area']
            del self.fields['from_area']

        if self.instance.type == Lift.LIFT:
            pass
           # self.fields['lift_width'].required = True
           # self.fields['lift_depth'].required = True
        elif areas:
            del self.fields['lift_width']
            del self.fields['lift_depth']
            del self.fields['intermediate_area1']
            del self.fields['intermediate_area2']
            del self.fields['visually_impaired_ok']

        if self.instance.type != Lift.STAIR:
            del self.fields['number_of_steps']
            del self.fields['steps_height']

        if self.instance.type not in (Lift.STAIR, Lift.ESCALATOR):
            del self.fields['handrail']
            del self.fields['handrail_height']

        if self.instance.type != Lift.ESCALATOR:
            del self.fields['pathway_mode']
        else:
            self.fields['handrail'].choices = (
                (3, "Both"),
            )

        if self.instance.type != Lift.STAIRLIFT:
            del self.fields['assistance_required']

    class Meta:
        model = Lift
        exclude = ['stop', 'type']


class ServicesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('save', 'Save', css_class='btn btn-success me-4'))
        self.helper.add_input(
            Submit('delete', 'Delete', css_class='btn btn-danger'))
    

        lines = Line.objects.filter(stations__station = self.instance.platform.parent_station)
        self.fields['line'].queryset = lines
    
        locations = Stop.objects.filter(location_type = 4, parent_station = self.instance.platform.pk)
        self.fields['location_of_level_access'].queryset = locations

        self.helper.layout = Layout(
            Row(
                Column('line', css_class='col-6 col-sm-4 flex-grow-1'),
               # Column('direction_towards', css_class='col-6 col-sm-4 flex-grow-1'),
            ),
            Row(
                HTML(
                    '<p class=" text-secondary mb-1 mt-4">Gap means distance between the platform and the train entrance</p>'
                ),
                Column('min_gap', css_class='col-6 col-sm-4 flex-grow-1'),
                Column('max_gap', css_class='col-6 col-sm-4 flex-grow-1'), 
                Column('average_gap', css_class='col-6 col-sm-4 flex-grow-1')
            ),
            Row(
                HTML(
                    '<p class="text-secondary mb-1 mt-4">Step means height between the platform and the train entrance</p>'
                ),
                Column('min_step', css_class='col-6 col-sm-4 flex-grow-1'), 
                Column('max_step', css_class='col-6 col-sm-4 flex-grow-1'), 
                Column('average_step', css_class='col-6 col-sm-4 flex-grow-1')
            ),
            Row(
                Column('designated_level_access_point', css_class='form-check form-switch'),
                Column('level_access_by_manual_ramp', css_class='form-check form-switch'),
            ),
            Row('location_of_level_access'),
            Row('additional_accessibility_info')
        )
    class Meta:
        model = Services
        exclude = ['platform', 'direction_towards']
        widgets = {
            'additional_accessibility_info': forms.Textarea(attrs={
                'rows': 2
            })
        }

class LineForm(ModelForm):
    stations = forms.ModelMultipleChoiceField(queryset=Stop.objects.filter(location_type=Stop.STATION))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('save', 'Save', css_class='btn btn-success me-4'))
        self.helper.add_input(
            Submit('delete', 'Delete', css_class='btn btn-danger'))
        

    class Meta:
        model = Line
        widgets = {
            'color': forms.TextInput(attrs={'type':'color', 'list':'presetColors'})
        }
        fields = '__all__'



class SameLevelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('save', 'Save', css_class='btn btn-success me-4'))
        if self.instance.pk:
            self.helper.add_input(
                Submit('delete', 'Delete', css_class='btn btn-danger'))
        
        areas = Stop.objects.filter(location_type = 5, parent_station = self.instance.station)

        self.fields['from_area'].queryset = areas
        self.fields['to_area'].queryset = areas

    class Meta:
        model = RampLevelPath
        exclude = ['station']
from django.forms import ModelForm
from .models import *

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit, Row, Column
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
        if self.instance.location_type == 0:
            self.fields['platform_code'].required = True
            self.fields['cardinal_direction'].required = True
            doors = Stop.objects.filter(location_type = 2, parent_station = self.instance.parent_station)
            if doors:
                self.fields['accessible_entrance_id'].queryset = doors
            else:
                del self.fields['accessible_entrance_id']
                
        if self.instance.location_type != 0:
            del self.fields['accessible_entrance_id']
            del self.fields['accessible_exit_id']
            del self.fields['step_free_route_information_available']
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
                Column('parent_station'),
                Column('location_type')
            ),
            Row(
                Column('code', css_class='col-sm-1 col-3'),
                Column('name', css_class='col-sm-11 col-9')
            ),
            Row(
                Column('desc', css_class='col-12')
            ),
            Row(
                'lat', 'lon'
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


class LiftForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('save', 'Save', css_class='btn btn-success me-4'))
        self.helper.add_input(Submit('delete', 'Delete', css_class='btn btn-danger'))

    class Meta:
        model = Lift
        fields = '__all__'

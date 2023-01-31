from django.forms import ModelForm
from .models import *

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit,Row, Column
from crispy_forms.bootstrap import StrictButton

class StopForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('parent_station')
            ),
            Row(
                Column('code', css_class='col-sm-1 col-3'),
                Column('name', css_class='col-sm-11 col-9')
            ),
            Row(
                Column('desc', css_class='col-12')
            ),
            Row(
                Column('wheelchair_boarding', css_class='col-sm-2 col-12'),
                Column('visually_impaired_path', css_class='col-sm-2 col-12')
            ),
            Row(
                Column('platform_code', css_class='col-sm-2 col-12'),
                Column('cardinal_direction', css_class='col-sm-2 col-12')
            ),
            Row(
                Column('accessible_entrance_id', css_class='col-sm-2 col-12'),
                Column('accessible_exit_id', css_class='col-sm-2 col-12')
            ),
            Row(
                Column('outside_station_unique_id')
            ),
            Field('wifi', css_class="form-check-input", wrapper_class="form-check form-switch"),
            Field('blue_badge_car_parking', css_class="form-check-input", wrapper_class="form-check form-switch"),
            Field('blue_badge_car_park_spaces', css_class="form-check-input", wrapper_class="form-check form-switch"),
            Field('taxi_ranks_outside_station', css_class="form-check-input", wrapper_class="form-check form-switch"),
            Field('bus_stop_outside_station', css_class="form-check-input", wrapper_class="form-check form-switch"),
            Field('train_station', css_class="form-check-input", wrapper_class="form-check form-switch"),
            StrictButton('<i class="fas fa-paper-plane"></i> Save', type="submit", name="save", css_class='btn btn-success me-4'),
            StrictButton('<i class="fas fa-trash"></i> Delete', type="submit", name="delete", css_class='btn btn-danger'),
        )


    class Meta:
        model = Stop
        fields = '__all__'
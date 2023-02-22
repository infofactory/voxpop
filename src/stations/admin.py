from django.contrib import admin

from .models import *


class StopAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'get_location_type_display']
admin.site.register(Stop, StopAdmin)


admin.site.register(Lift)
admin.site.register(RampRoutes)
admin.site.register(RampLevelPath)
admin.site.register(StepFreeInterchangeInfo)
admin.site.register(Services)



class LineStationInline(admin.TabularInline):
    model = LineStation

class LineAdmin(admin.ModelAdmin):
    inlines = [
        LineStationInline,
    ]
admin.site.register(Line, LineAdmin)

admin.site.site_header = 'Accedi a Voxpop'
admin.site.site_title = 'Voxpop'
admin.site.index_title = 'Voxpop'
admin.site.site_url = '/stops/'
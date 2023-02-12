from django.contrib import admin

from .models import *

admin.site.register(Stop)
admin.site.register(Lift)
admin.site.register(RampRoutes)
admin.site.register(RampLevelPath)
admin.site.register(StepFreeInterchangeInfo)
admin.site.register(Services)
admin.site.register(Line)



class RouteStationInline(admin.TabularInline):
    model = RouteStation

class RouteAdmin(admin.ModelAdmin):
    inlines = [
        RouteStationInline,
    ]
admin.site.register(Route, RouteAdmin)

admin.site.site_header = 'Accedi a Voxpop'
admin.site.site_title = 'Voxpop'
admin.site.index_title = 'Voxpop'
admin.site.site_url = '/stops/'
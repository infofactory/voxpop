from django.contrib import admin

from .models import *

admin.site.register(Stop)
admin.site.register(Lift)
admin.site.register(Stairlift)
admin.site.register(Stair)
admin.site.register(Escalator)
admin.site.register(RampRoutes)
admin.site.register(RampLevelPath)
admin.site.register(StepFreeInterchangeInfo)
admin.site.register(PlatformService)

from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Membership)
admin.site.register(WorkoutPlan)
admin.site.register(WorkoutLog)
admin.site.register(DietPlan)
admin.site.register(Attendance)

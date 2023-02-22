from django.contrib import admin
from users.models import Appointment, Doctor, Patient, User

admin.site.register(Appointment)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(User)

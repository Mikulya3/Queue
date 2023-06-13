from django.contrib import admin
from apps.talon.models import Ticket, OutherTalon, CallCustomerTask

admin.site.register(Ticket)
admin.site.register(CallCustomerTask)
admin.site.register(OutherTalon)


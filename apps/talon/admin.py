from django.contrib import admin
from apps.talon.models import Ticket, OutherTalon, CallCustomerTask, TicketArchive

admin.site.register(Ticket)
admin.site.register(CallCustomerTask)
admin.site.register(OutherTalon)
admin.site.register(TicketArchive)


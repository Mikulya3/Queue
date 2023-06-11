from django.contrib import admin
from apps.talon.models import Ticket, TicketHistory

admin.site.register(Ticket)
admin.site.register(TicketHistory)
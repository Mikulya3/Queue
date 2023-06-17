from django.contrib import admin

from apps.queue.models import Queue
from apps.queue.models import ReservedTicket
from apps.queue.models import Ticket
from apps.queue.models import TicketHistory

admin.site.register(Queue)
admin.site.register(ReservedTicket)
admin.site.register(Ticket)
admin.site.register(TicketHistory)
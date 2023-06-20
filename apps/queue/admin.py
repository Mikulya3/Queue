from django.contrib import admin

from apps.queue.models import Queue
from apps.queue.models import ReservedTicket
from apps.queue.models import Ticket
from apps.queue.models import TicketHistory

from . import models
from import_export.admin import ImportExportModelAdmin

class ticketAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    ...
class reservedticketAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    ...

class tickethistoryAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    ...
admin.site.register(models.ReservedTicket,reservedticketAdmin)
admin.site.register(models.Ticket,ticketAdmin)
admin.site.register(models.TicketHistory,tickethistoryAdmin)
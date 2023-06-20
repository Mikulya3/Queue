from django.contrib import admin

from . import models
from import_export.admin import ImportExportModelAdmin


class clientAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    ...
class reservedTicketAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    ...

class reviewAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    ...
admin.site.register(models.Review,reviewAdmin)
admin.site.register(models.Client,clientAdmin)
admin.site.register(models.ReservedTicket,reservedTicketAdmin)
from django.contrib import admin
from . import models
from import_export.admin import ImportExportModelAdmin


class bankAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    ...
class branchAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    ...


admin.site.register(models.Bank,bankAdmin)
admin.site.register(models.Branch,branchAdmin)

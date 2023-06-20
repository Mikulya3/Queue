from . import models
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


class operatorAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['user', 'is_available', 'branch']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    list_filter = ['is_available', 'branch']

admin.site.register(models.Operator,operatorAdmin)
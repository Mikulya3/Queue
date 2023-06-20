from django.contrib import admin

from apps.manager.models import Managers


@admin.register(Managers)
class ManagerAdmin(admin.ModelAdmin):

    fieldsets = (
        ('Personal Info', {'fields': ('first_name', 'last_name','position','window_number', 'note','is_blocked')}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
        ('Important dates', {'fields': ('last_login',  'email', 'date_joined')}),
    )


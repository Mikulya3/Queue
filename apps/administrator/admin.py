from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from apps.account.models import QueueUser
from apps.operators.models import Operator
from apps.queue.models import Queue






User = get_user_model()

@admin.register(QueueUser)
class QueueUserAdmin(UserAdmin):
    ACCESS_LEVELS = {
        'administrator': 'full_access',
        'operator': 'partial_access',
        'consultant': 'read_only',
        'manager': 'limited_access'
    }
    list_display = ['username', 'first_name', 'middle_name', 'last_name', 'position', 'window_number', 'is_blocked']
    search_fields = ['username', 'first_name', 'middle_name', 'last_name', 'position', 'window_number', 'is_blocked']
    list_filter = ['position', 'is_blocked']
    ordering = ['username']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'middle_name', 'last_name', 'email', 'position')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional Info', {'fields': ('window_number', 'note', 'access_level', 'is_blocked')}),
    )

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):


    list_display = ['name', 'queue_type', 'average_service_time','max_auto_automatic_calling', 'max_service_time']
    search_fields = ['name', 'queue_type', 'operator']
    list_filter = ['queue_type']
    exclude = ('created_at',)
    fieldsets = (
        ('General', {
            'fields': ('branch', 'name', 'queue_type', 'priority','description', 'operator')
        }),
        ('Time', {
            'fields': ('start_of_day', 'end_of_day', 'queue_start_time','max_auto_automatic_calling','queue_end_time')
        }),
        ('Service', {
            'fields': ('queue_length', 'standard_service_time', 'is_automatic_calling_enabled', 'priority_service_time', 'vip_service_time')
        }),
        ('Statistics', {
            'fields': ('average_service_time', 'max_service_time')
        }),
        ('Calendars', {
            'fields': ('general_calendar', 'individual_calendar'),
        }),
    )


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_available', 'branch']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    list_filter = ['is_available', 'branch']
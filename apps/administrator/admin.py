
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()
class QueueUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'position', 'window_number', 'is_blocked']
    search_fields = ['email', 'first_name', 'last_name', 'position', 'window_number']
    list_filter = ['position', 'is_blocked']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Additional Info', {'fields': ('position', 'window_number', 'note', 'access_level', 'is_blocked')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(User, QueueUserAdmin)

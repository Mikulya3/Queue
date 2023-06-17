from django.contrib import admin

from apps.client.models import Client
from apps.client.models import ReservedTicket
from apps.client.models import Review

admin.site.register(Client)
admin.site.register(ReservedTicket)
admin.site.register(Review)


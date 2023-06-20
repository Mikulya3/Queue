from django.contrib import admin

from apps.equipment.models import Television
from apps.equipment.models import Terminal
from apps.equipment.models import MobileApp
from apps.equipment.models import Website

admin.site.register(Television)
admin.site.register(Terminal)
admin.site.register(MobileApp)
admin.site.register(Website)


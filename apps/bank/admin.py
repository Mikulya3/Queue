from django.contrib import admin

from apps.bank.models import Bank
from apps.bank.models import Branch

admin.site.register(Bank)
admin.site.register(Branch)

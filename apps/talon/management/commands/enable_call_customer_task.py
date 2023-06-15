from django.core.management.base import BaseCommand
from apps.talon.models import CallCustomerTask

class Command(BaseCommand):
    help = 'Enable the call_customer task'

    def handle(self, *args, **options):
        call_customer_task = CallCustomerTask.objects.first()
        if call_customer_task:
            call_customer_task.enabled = True
            call_customer_task.save()
            self.stdout.write(self.style.SUCCESS('call_customer task has been enabled.'))
        else:
            self.stdout.write(self.style.ERROR('call_customer task does not exist.'))

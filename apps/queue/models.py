from django.utils import timezone
from apps.client.models import Client
from django.db import models
from apps.bank.models import Branch
from apps.operators.models import Operator
from datetime import timedelta, datetime


class QueueType(models.TextChoices):
    STANDARD = 'standard', 'Standard Queue'
    PRIORITY = 'priority', 'Priority Queue'
    VIP = 'vip', 'VIP Queue'


class TicketType(models.TextChoices):
    STANDARD = 'standard', 'Standard Ticket'
    PRIORITY = 'priority', 'Priority Ticket'
    VIP = 'vip', 'VIP Ticket'


class Queue(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    queue_type = models.CharField(max_length=20, choices=QueueType.choices, default=QueueType.STANDARD)
    priority = models.BooleanField(default=False)
    queue_length = models.IntegerField(default=0)  # Добавлено поле queue_length
    standard_service_time = models.DurationField()
    priority_service_time = models.DurationField()
    vip_service_time = models.DurationField()
    max_limit = models.IntegerField(default=1000)
    is_paused = models.BooleanField(default=False)  # Добавлено поле is_paused
    max_waiting_time = models.PositiveIntegerField(default=0)

    def get_service_time(self, ticket_type):
        if ticket_type == TicketType.STANDARD:
            return self.standard_service_time
        elif ticket_type == TicketType.PRIORITY:
            return self.priority_service_time
        elif ticket_type == TicketType.VIP:
            return self.vip_service_time
        else:
            return self.standard_service_time  # Значение по умолчанию

    def calculate_current_waiting_time(self):
        # Логика расчета текущего времени ожидания в очереди
        now = timezone.now()
        tickets = Ticket.objects.filter(queue=self, status='waiting')
        total_waiting_time = sum((now - ticket.created_at).total_seconds() for ticket in tickets)
        average_waiting_time = total_waiting_time / tickets.count() if tickets.count() > 0 else 0
        return average_waiting_time

    def __str__(self):
        return self.name


class ReservedTicket(models.Model):
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name='reserved_tickets')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reserved_tickets')
    ticket_number = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    service_time = models.TimeField()

    def __str__(self):
        return self.ticket_number


class Ticket(models.Model):
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    ticket_number = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_time = models.DateTimeField()
    language = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    served_at = models.DateTimeField(blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)  # Замените user на client
    TicketType = models.TextChoices('TicketType', 'STANDARD PRIORITY VIP')
    priority = models.CharField(max_length=10, choices=TicketType.choices, default=TicketType.STANDARD)
    service_time = models.DurationField(default=timedelta(minutes=0))
    wait_time = models.DurationField(blank=True, null=True)



    def is_ticket_active(self):
        return self.expiration_time >= timezone.now()

    def save(self, *args, **kwargs):
        if self.status == 'served' and self.served_at is not None:
            self.wait_time = self.served_at - self.created_at
        elif self.status == 'waiting':
            self.wait_time = datetime.now() - self.created_at
        else:
            self.wait_time = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ticket_number

class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    operation = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)

    def __str__(self):
        return f"Ticket: {self.ticket.ticket_number}, Operation: {self.operation}"

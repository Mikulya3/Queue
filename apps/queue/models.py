from django.core.exceptions import ValidationError
from django.db.models import F
from django.utils import timezone
from apps.client.models import Client
from apps.bank.models import Branch
from datetime import timedelta, datetime, date
from apps.operators.models import Operator
from django.db import models




class QueueType(models.TextChoices):
    STANDARD = 'standard', 'Standard Queue'
    PRIORITY = 'priority', 'Priority Queue'
    VIP = 'vip', 'VIP Queue'


class TicketType(models.TextChoices):
    STANDARD = 'standard', 'Standard Ticket'
    PRIORITY = 'priority', 'Priority Ticket'
    VIP = 'vip', 'VIP Ticket'

class Queue(models.Model):
    GENERAL_CALENDAR_CHOICES = [
        ('normal','Normal'),
        ('holiday', 'Holiday'),
        ('weekend', 'Weekend'),
        ('half-day', 'Half-day'),
    ]
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    queue_type = models.CharField(max_length=20, choices=QueueType.choices, default=QueueType.STANDARD)
    priority = models.BooleanField(default=False)
    queue_length = models.IntegerField(default=0)  # Добавлено поле queue_length
    standard_service_time = models.DurationField(null=True, blank=True)
    priority_service_time = models.DurationField(null=True, blank=True)
    vip_service_time = models.DurationField(null=True,blank=True)
    max_limit = models.IntegerField(default=1000)
    is_paused = models.BooleanField(default=False)  # Добавлено поле is_paused
    max_waiting_time = models.PositiveIntegerField(default=0)
    average_service_time = models.IntegerField(blank=True)#среднее  время обслуживания(в минутах);
    max_service_time = models.IntegerField(blank=True,null=True) #максимальное время обслуживания(в минутах);
    start_of_day = models.TimeField(blank=True,null=True) # начало  рабочего дня;
    end_of_day = models.TimeField(blank=True,null=True) # окончание рабочего дня;
    description = models.TextField() # описание очереди;
    queue_start_time = models.TimeField(blank=True,null=True) #установка времени начала  для каждой очереди;
    queue_end_time = models.TimeField(blank=True,null=True) #установка окончания выдачи талонов для каждой очереди;
    operator = models.ForeignKey('operators.Operator', on_delete=models.CASCADE, related_name='assigned_queues')
    general_calendar = models.CharField(max_length=20,choices=GENERAL_CALENDAR_CHOICES,default='normal')
    individual_calendar = models.DateField(blank=True, null=True)
    is_automatic_calling_enabled = models.BooleanField(default=True)#включение/отключение режима автоматического вызова клиентов к операторам;
    max_auto_automatic_calling = models.PositiveIntegerField(default=0) #установка максимального количества автоматических переносов, после которых талон удаляется из очереди;

    def save(self, *args, **kwargs):
        if self.operator.is_blocked:
            raise ValidationError('Заблокированный оператор не может обслуживать  очередь!')
        else:
            super().save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if self.general_calendar != 'normal' and self.individual_calendar:
            current_date = timezone.now().date()
            if self.individual_calendar == current_date and self.general_calendar == 'holiday':
                raise ValidationError('Сегодня праздник, не рабочий день')
            if self.individual_calendar < current_date:
                raise ValidationError('Очередь не может быть создана прошедшим числом')
            elif self.individual_calendar.weekday() >= 5:
                raise ValidationError('Банк в выходные не работает')
        super().save(*args, **kwargs)
    def is_within_calendar(self):
        current_date = date.today()
        if self.general_calendar:
            return current_date == self.general_calendar
        elif self.individual_calendar:
            return current_date == self.individual_calendar
        else:
            return True
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

    def save(self, *args, **kwargs):
        if self.queue.queue_start_time and self.queue.queue_end_time:
            if self.created_at < self.queue.queue_start_time or self.created_at > self.queue.queue_end_time:
                raise ValueError("Ticket cannot be created outside the queue start and end times.")
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        current_time = timezone.localtime()

        if self.queue.queue_end_time and self.queue.queue_end_time < current_time.time():
            raise ValidationError("Выдача талонов для данной очереди уже завершена.")

        if self.queue.queue_start_time and self.queue.queue_start_time > current_time.time():
            raise ValidationError("Выдача талонов для данной очереди еще не началась.")
    def automatic_calling(ticket):
        ticket.queue.automatic_calling = F('automatic_calling')+1
        ticket.queue.save()
        if ticket.automatic_calling  >= ticket.queue.max_auto_automatic_calling:
            ticket.delete()




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



from django.db import models
from apps.operators.models import Operator

STATUS_CHOICES = (
    ('completed', 'Обслужен'),
    ('cancelled', 'Не обслужен'),
)


class Ticket(models.Model):
    number = models.CharField(max_length=10, unique=True)  # Поле для присваивания номера
    created_at = models.DateTimeField(auto_now_add=True)
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Ticket {self.number}"

class TicketHistory(models.Model):
    STATUS_COMPLETED = 'Обслужен'
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    completed_at = models.DateTimeField(auto_now_add=True)


    # Дополнительные поля, связанные с историей талона

    class Meta:
        ordering = ['-completed_at']



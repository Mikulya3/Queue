from django.db import models
from apps.operators.models import Operator
from django.db.models.signals import pre_save
from django.dispatch import receiver


STATUS_CHOICES = (
    ('completed', 'Обслужен'),
    ('cancelled', 'Не обслужен'),
)


class Ticket(models.Model):
    number = models.CharField(max_length=1000, unique=True)  # Поле для присваивания номера
    created_at = models.DateTimeField(auto_now_add=True)
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_veteran = models.BooleanField(default=False)
    failed_attempts = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['id']



    def __str__(self):
        return f"Ticket {self.number}"


class OutherTalon(models.Model):
    number = models.CharField(max_length=1000)
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField(blank=True)
    end_time = models.DateTimeField(null=True, blank=True)



class CallCustomerTask(models.Model):
    enabled = models.BooleanField(default=False)


from django.db import models
from django.conf import settings
#from django.contrib.auth.models import User
from apps.bank.models import Branch
from django.core.validators import MinValueValidator, MaxValueValidator
#from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission, UserManager


class Client(AbstractUser):


    # Дополнительные поля для модели Client
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=100)

    # Обратная связь с моделью Group
    groups = models.ManyToManyField(Group, related_name='client_users', blank=True)

    # Обратная связь с моделью Permission
    user_permissions = models.ManyToManyField(Permission, related_name='client_users', blank=True)

    objects = UserManager()

    # Дополнительные методы или поведение модели Client

    def __str__(self):
        return self.username

class ReservedTicket(models.Model):
    queue = models.ForeignKey('queue.Queue', on_delete=models.CASCADE)  # Замена импорта на строковое имя модели
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    ticket_number = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ticket_number

class Review(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField()

    def __str__(self):
        return f"Review for Branch {self.branch.name}"



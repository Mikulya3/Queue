from django.db import models

from apps.account.models import QueueUser
from apps.bank.models import Branch
from config import settings


class Operator(models.Model):
    user = models.OneToOneField(QueueUser, on_delete=models.CASCADE, related_name='operator')
    is_available = models.BooleanField(default=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)



    def __str__(self):
        return self.user.username

    @property
    def position(self):
        return self.user.position

    @property
    def window_number(self):
        return self.user.window_number

    @property
    def email(self):
        return self.user.email

    @property
    def note(self):
        return self.user.note

    @property
    def access_level(self):
        return self.user.access_level

    @property
    def is_blocked(self):
        return self.user.is_blocked


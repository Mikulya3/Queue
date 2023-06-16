from django.db import models

from apps.account.models import QueueUser
from apps.bank.models import Branch



class Operator(models.Model):
    name = models.ForeignKey(QueueUser, on_delete=models.CASCADE, related_name='operators')
    is_available = models.BooleanField(default=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)




    def window_number(self):
        return self.name.window_number

    def email(self):
        return self.name.email

    def position(self):
        return self.name.position

    def __str__(self):
        return f"Operator: {self.name.first_name} (Window: {self.name.window_number})"






from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

class Managers(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operators')
    is_available = models.BooleanField(default=True)
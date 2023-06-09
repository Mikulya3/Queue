from django.db import models


class Operator(models.Model):
    name = models.CharField(max_length=100)
    window_number = models.IntegerField()
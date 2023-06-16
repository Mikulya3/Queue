from django.db import models
from apps.bank.models import Bank, Branch

# Create your models here.

class Television(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    screen_size = models.CharField(max_length=20)
    resolution = models.CharField(max_length=20)
    smart_tv = models.BooleanField(default=False)
    wifi_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.brand} {self.model}"


class Terminal(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    software_version = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class MobileApp(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    platform = models.CharField(max_length=50)
    developer = models.CharField(max_length=100)
    release_date = models.DateField()

    def __str__(self):
        return self.name


class Website(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.URLField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
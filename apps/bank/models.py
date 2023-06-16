from django.db import models

# Create your models here.
class Bank(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    established_date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return self.name


class Branch(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    branch_director_name = models.CharField(max_length=100)
    branch_director_name_number = models.CharField(max_length=15)
    status = models.CharField(max_length=50)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    description = models.TextField()

    def __str__(self):
        return self.name
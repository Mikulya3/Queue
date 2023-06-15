from django.db import models
from django.contrib.auth.models import User
from loguru import logger

#
# class Ticket(models.Model):
#     number = models.CharField(max_length=1000, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
#     is_veteran = models.BooleanField(default=False)
#     failed_attempts = models.PositiveIntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_completed = models.BooleanField(default=False)
#     status = models.CharField(max_length=255)
#     status_signal = models.BooleanField(default=False)
#     queue= models.BooleanField(default=False)
#     can_modify_queue_list = models.BooleanField(default=False)
#     can_create_tickets = models.BooleanField(default=False)
#     can_close_tickets = models.BooleanField(default=False)
#
#     class Meta:
#         ordering = ['id']
#
#     def __str__(self):
#         return f"Ticket {self.number}"
#
#     def save(self, *args, **kwargs):
#         logger.info(f'Ticket {self.number} saved')
#         super().save(*args, **kwargs)
#
#     def grant_permissions(self, operator, can_call_out_of_turn=False, can_modify_queue_list=False,
#                           can_create_tickets=False, can_close_tickets=False):
#         self.operator = operator
#         self.can_call_out_of_turn = can_call_out_of_turn
#         self.can_modify_queue_list = can_modify_queue_list
#         self.can_create_tickets = can_create_tickets
#         self.can_close_tickets = can_close_tickets
#         self.save()
# class Queue(models.Model):
#     name = models.CharField(max_length=255)
#     ticket_numbers = models.ManyToManyField('Ticket')
#
#     def __str__(self):
#         return self.name
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.account.managers import UserManager


class QueueUser(AbstractUser):
    POSITION_CHOICES = (
        ('admin','Administrator'),
        ('operator','Operator')
    )
    AUTH_MODE_CHOICES = (
        ('domain', 'Domain'),
        ('embedded', 'Embedded'),
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    Last_name = models.CharField(_("last name"), max_length=150, blank=True)
    middle_name = models.CharField(_("middle_name"), max_length=150, blank=True)
    position = models.CharField(_("positions"),max_length=100, choices=POSITION_CHOICES)
    window_number = models.CharField(_("window number"), max_length=100)
    note = models.TextField(_("note"),blank=True)
    auth_mode = models.CharField(max_length=100, choices=AUTH_MODE_CHOICES)
    blocked = models.BooleanField(default=False)
    access_level = models.CharField(max_length=100)
    call_outside_queue = models.BooleanField(default=False)
    modify_queue_list = models.BooleanField(default=False)
    create_and_close_tickets = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    activation_code = models.CharField(max_length=40, blank=True)
    domain_auth = models.BooleanField(default=True)
    username = models.CharField(max_length=100,unique=True)
    is_blocked = models.BooleanField(default=False)
    access_level = models.CharField(max_length=100)

    def block_user(self):
        self.is_blocked = True
        self.save()

    def unblock_user(self):
        self.is_blocked = False
        self.save()

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def create_activation_code(self):
        import uuid
        code = str(uuid.uuid4())
        self.activation_code = code
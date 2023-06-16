from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.account.managers import UserManager

POSITION_CHOICES = (
        ('administrator','Administrator'),
        ('operator','Operator'),
        ('consultant', 'Consultant'),
        ('manager','Manager')
    )

ACCESS_LEVELS = {
        'administrator': 'full_access',
        'operator': 'partial_access',
        'consultant': 'read_only',
        'manager': 'limited_access'
    }

class QueueUser(AbstractUser,PermissionsMixin):
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    Last_name = models.CharField(_("last name"), max_length=150, blank=True)
    middle_name = models.CharField(_("middle_name"), max_length=150, blank=True)
    position = models.CharField(_("position"),max_length=100, choices=POSITION_CHOICES)
    window_number = models.CharField(_("window number"), max_length=100)
    note = models.TextField(_("note"),blank=True)
    access_level = models.CharField(_("ACCESS_LEVELS"), max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    activation_code = models.CharField(max_length=40, blank=True)
    username = models.CharField(max_length=100,unique=True)
    is_blocked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    def block_user(self):
        self.is_blocked = True
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
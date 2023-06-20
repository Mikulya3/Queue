from django.db import models
from django.contrib.auth.models import User
from loguru import logger

from apps.account.models import QueueUser
from apps.bank.models import Branch
from apps.queue.models import Queue
from config import settings



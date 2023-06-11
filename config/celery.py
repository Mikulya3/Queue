import os
import django
from celery import Celery
from django.conf import settings



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
app = Celery('config')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)



# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создание экземпляра Celery
app = Celery('config')

# Загрузка настроек Celery из файла settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Установка параметра broker_connection_retry_on_startup
app.conf.update(
    broker_connection_retry_on_startup=True
)

# Автоматическое обнаружение и регистрация задач
app.autodiscover_tasks()


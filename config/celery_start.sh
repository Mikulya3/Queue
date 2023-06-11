#!/bin/bash

# Перейти в директорию вашего проекта
cd /home/lenova/Desktop/rsk2/queue-master/

# Активировать виртуальное окружение, если используется
source /home/lenova/Desktop/rsk2/queue-master/venv/bin/python
/venv/bin/activate

# Запуск Celery Worker
celery -A config.celery worker --loglevel=info &

# Запуск Celery Beat
celery -A config.celery beat --loglevel=info &
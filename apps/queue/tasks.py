from celery import shared_task
from django.core.mail import send_mail
from apps.queue.models import Queue, Ticket

@shared_task
def send_notification_email(recipient_email, subject, message):
    send_mail(subject, message, 'noreply@yourdomain.com', [recipient_email])

@shared_task
def call_next_ticket(queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        next_ticket = Ticket.objects.filter(queue=queue, status='waiting').order_by('created_at').first()
        if next_ticket:
            next_ticket.status = 'called'
            next_ticket.save()
    except Queue.DoesNotExist:
        pass

@shared_task
def schedule_ticket_processing(queue_id, interval_minutes):
    call_next_ticket.apply_async((queue_id,), countdown=interval_minutes * 60)

# Для запуска периодической обработки:
# schedule_ticket_processing.delay(queue_id, interval_minutes)
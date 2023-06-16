from celery import shared_task
from django.core.mail import send_mail
from apps.queue.models import Queue, Ticket
from config.celery import app

@app.task
def send_notification_email(client_email, ticket_number):
    print(f"Sending email to {client_email} with ticket number {ticket_number}")
    send_mail(
        'Ваш номер талона',
        f'Ваш номер талона: {ticket_number}',
        'evelbrus2@gmail.com',
        [client_email],
        fail_silently=True,
    )




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
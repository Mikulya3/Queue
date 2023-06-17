from celery import shared_task
from django.core.mail import send_mail
from apps.queue.models import Queue, Ticket
from config.celery import app
from apps.operators.models import Operator
from apps.queue.serializers import TicketSerializer
from datetime import timedelta


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

@app.task
def call_next_available_operator_auto_task(queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        next_ticket = Ticket.objects.filter(queue=queue, status='waiting').order_by('created_at').first()

        if next_ticket:
            operator = Operator.objects.filter(is_available=True).exclude(id__in=Ticket.objects.filter(status='called').values('operator')).first()

            if operator:
                next_ticket.status = 'called'
                next_ticket.operator = operator
                next_ticket.save()

                # Обновляем статус доступности оператора
                operator.is_available = False
                operator.save()

                # Вычисляем количество операторов и сколько из них заняты
                total_operators = Operator.objects.count()
                busy_operators = Operator.objects.filter(is_available=False).count()

                # Создаем задачу для вызова следующего доступного оператора через определенное время
                interval = timedelta(seconds=10)
                call_next_available_operator_auto_task.apply_async((queue_id,), countdown=interval.total_seconds())

                # Возвращаем данные о билете
                serializer = TicketSerializer(next_ticket)
                response_data = serializer.data
                response_data['total_operators'] = total_operators
                response_data['busy_operators'] = busy_operators
                return response_data

        return {'message': 'No more tickets in the queue'}

    except Queue.DoesNotExist:
        return {'message': 'Queue does not exist'}

    except Operator.DoesNotExist:
        return {'message': 'Operator does not exist'}


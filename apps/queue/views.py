from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.bank.models import Branch
from apps.queue.models import Queue, Ticket, ReservedTicket, TicketHistory
from apps.client.models import Client
from apps.operators.models import Operator
from apps.queue.serializers import QueueSerializer, TicketSerializer, TicketHistorySerializer
from apps.bank.serializers import BranchSerializer
from apps.client.serializers import ReviewSerializer, ReservedTicketSerializer
from apps.operators.serializers import OperatorSerializer
from datetime import datetime, timedelta
from django.utils import timezone
from random import randint
from django.db.models import Avg, F
from apps.queue.tasks import send_notification_email
import csv
from django.http import HttpResponse
#from twilio.rest import Client
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from datetime import time


@api_view(['POST'])
def create_queue(request):
    serializer = QueueSerializer(data=request.data)
    if serializer.is_valid():
        queue = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_queue(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        queue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def update_queue(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        serializer = QueueSerializer(queue, data=request.data)
        if serializer.is_valid():
            max_waiting_time = serializer.validated_data.get('max_waiting_time')
            if max_waiting_time is not None:
                queue.max_waiting_time = max_waiting_time
            # Остальная логика сохранения обновленных данных
            queue.save()
            serializer = QueueSerializer(queue)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_all_queues(request):
    queues = Queue.objects.all()
    serializer = QueueSerializer(queues, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_queue(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        serializer = QueueSerializer(queue)
        return Response(serializer.data)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_tickets_in_queue(request, queue_id):
    try:
        # Получите все обычные билеты в очереди
        tickets = Ticket.objects.filter(queue_id=queue_id)

        # Получите все зарезервированные билеты в очереди
        reserved_tickets = ReservedTicket.objects.filter(queue_id=queue_id)

        # Сериализация обычных билетов
        ticket_serializer = TicketSerializer(tickets, many=True)

        # Сериализация зарезервированных билетов
        reserved_ticket_serializer = ReservedTicketSerializer(reserved_tickets, many=True)

        # Объединение сериализованных данных обычных и зарезервированных билетов
        serialized_data = ticket_serializer.data + reserved_ticket_serializer.data

        return Response(serialized_data)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_queue_status(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        ticket_count = Ticket.objects.filter(queue=queue).count()
        # Расчет времени ожидания - требуется дополнительная логика
        # Возвращаем информацию о состоянии очереди
        data = {
            'queue_id': queue.id,
            'ticket_count': ticket_count,
            # Дополнительные поля состояния очереди
        }
        return Response(data)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

def generate_ticket_number():
    return str(randint(1000, 9999))


@api_view(['POST'])
def generate_ticket(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)

        if queue.is_paused:
            return Response({'message': 'Cannot generate ticket. Queue is paused.'}, status=status.HTTP_400_BAD_REQUEST)

        ticket_number = generate_ticket_number()
        expiration_time = datetime.now() + timedelta(minutes=30)  # Истечение через 30 минут

        wait_time = None  # Инициализация времени ожидания

        # Расчет времени ожидания в зависимости от текущего состояния очереди и логики вашего приложения
        # wait_time = ...

        ticket = Ticket.objects.create(
            queue=queue,
            branch=queue.branch,
            ticket_number=ticket_number,
            created_at=datetime.now(),
            expiration_time=expiration_time,
            status='waiting',
            wait_time=wait_time,  # Присваивание времени ожидания
        )
        serializer = TicketSerializer(ticket)

        # Создание записи в истории билета
        history = TicketHistory.objects.create(ticket=ticket, action='Generated', timestamp=datetime.now())

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def call_next_ticket(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        next_ticket = Ticket.objects.filter(queue=queue, status='waiting').order_by('created_at').first()
        if next_ticket:
            next_ticket.status = 'called'
            next_ticket.save()
            serializer = TicketSerializer(next_ticket)

            # Создание записи в истории билета
            history = TicketHistory.objects.create(ticket=next_ticket, action='Called', timestamp=datetime.now())

            return Response(serializer.data)
        return Response({'message': 'No more tickets in the queue'}, status=status.HTTP_404_NOT_FOUND)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_ticket(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Ticket.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def move_ticket_to_queue(request, ticket_id, new_queue_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        new_queue = Queue.objects.get(id=new_queue_id)

        # Создание записи в истории билета
        history = TicketHistory.objects.create(ticket=ticket, action='Moved to Queue', timestamp=datetime.now())

        ticket.queue = new_queue
        ticket.branch = new_queue.branch
        ticket.save()
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)
    except (Ticket.DoesNotExist, Queue.DoesNotExist):
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def update_ticket_status(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        new_status = request.data.get('status')
        ticket.status = new_status
        if new_status == 'served':
            ticket.served_at = timezone.now()  # Установка текущего времени в served_at
        ticket.save()
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)
    except Ticket.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_waiting_tickets(request):
    tickets = Ticket.objects.filter(status='waiting')
    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_served_tickets(request):
    tickets = Ticket.objects.filter(status='served')
    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_total_tickets(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        ticket_count = Ticket.objects.filter(queue=queue).count()
        return Response({'ticket_count': ticket_count})
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def calculate_average_wait_time(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        served_tickets = Ticket.objects.filter(queue=queue, status='served', served_at__isnull=False)
        average_wait_time = served_tickets.aggregate(avg_wait_time=Avg(F('served_at') - F('created_at')))
        return Response({'average_wait_time': average_wait_time['avg_wait_time']})
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_branch_info(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        branch = queue.branch
        # Дополнительная логика для сериализации информации о филиале
        serializer = BranchSerializer(branch)
        return Response(serializer.data)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

def calculate_waiting_time_statistics(queue):
    served_tickets = Ticket.objects.filter(queue=queue, status='served')
    wait_time_data = served_tickets.values_list('wait_time', flat=True)

    wait_time_data_cleaned = [t.total_seconds() for t in wait_time_data if t is not None]
    min_wait_time = min(wait_time_data_cleaned) if wait_time_data_cleaned else None
    max_wait_time = max(wait_time_data_cleaned) if wait_time_data_cleaned else None
    avg_wait_time = sum(wait_time_data_cleaned) / len(wait_time_data_cleaned) if wait_time_data_cleaned else None

    statistics = {
        'min_wait_time': min_wait_time,
        'max_wait_time': max_wait_time,
        'avg_wait_time': avg_wait_time,
    }

    return statistics

@api_view(['GET'])
def view_waiting_time_statistics(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        # Дополнительная логика для получения статистики по времени ожидания
        statistics = calculate_waiting_time_statistics(queue)
        return Response(statistics)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def send_ticket_notification(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)

        if ticket.client is not None and ticket.client.email:
            recipient_email = ticket.client.email
            subject = 'Your ticket status has been updated'
            message = f'Your ticket number is: {ticket.ticket_number}'
            send_notification_email.delay(recipient_email, subject, message)
            return Response({'message': 'Notification sent'})
        else:
            return Response({'message': 'Client email is missing'}, status=status.HTTP_400_BAD_REQUEST)
    except Ticket.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def search_ticket_by_number(request, ticket_number):
    try:
        ticket = Ticket.objects.get(ticket_number=ticket_number)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)
    except Ticket.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def search_queues_by_branch(request, branch_id):
    try:
        queues = Queue.objects.filter(branch_id=branch_id)
        serializer = QueueSerializer(queues, many=True)
        return Response(serializer.data)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def search_queues_by_name(request):
    name = request.GET.get('name')
    if name:
        queues = Queue.objects.filter(name__icontains=name)
        serializer = QueueSerializer(queues, many=True)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def sort_queues(request, sort_by):
    if sort_by == 'name':
        queues = Queue.objects.order_by('name')
    elif sort_by == 'created_at':
        queues = Queue.objects.order_by('created_at')
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer = QueueSerializer(queues, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
def set_ticket_priority(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        priority = request.data.get('priority')

        if priority in [choice[0] for choice in Ticket.TicketType.choices]:
            ticket.priority = priority
            ticket.save()
            serializer = TicketSerializer(ticket)
            return Response(serializer.data)
        else:
            return Response({'error': 'Invalid priority value'}, status=status.HTTP_400_BAD_REQUEST)

    except Ticket.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def set_max_ticket_limit(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        max_limit = request.data.get('max_limit')
        queue.max_limit = max_limit
        queue.save()
        serializer = QueueSerializer(queue)
        return Response(serializer.data)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reserve_ticket(request, queue_id, client_id):
    try:
        queue = Queue.objects.get(id=queue_id)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        client = Client.objects.get(id=client_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    ticket_number = generate_ticket_number()

    # Получение значения service_time из запроса
    service_time = request.data.get('service_time')

    reserved_ticket = ReservedTicket.objects.create(
        queue=queue,
        client=client,
        ticket_number=ticket_number,
        service_time=service_time  # Использование введенного пользователем значения
    )

    serializer = ReservedTicketSerializer(reserved_ticket)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_ticket_remaining_time(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        remaining_time = ticket.expiration_time - timezone.now()
        return Response({'remaining_time': remaining_time.total_seconds()})
    except Ticket.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def submit_review(request):
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        review = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_available_operators(request, queue_id):
    try:
        operators = Operator.objects.filter(queue_id=queue_id, available=True)
        serializer = OperatorSerializer(operators, many=True)
        return Response(serializer.data)
    except Operator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def export_queue_data(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        tickets = Ticket.objects.filter(queue=queue)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{queue.name}_tickets.csv"'

        writer = csv.writer(response)
        writer.writerow(['Ticket Number', 'Created At', 'Status'])

        for ticket in tickets:
            writer.writerow([ticket.ticket_number, ticket.created_at, ticket.status])

        return response
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_ticket_history(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        history = TicketHistory.objects.filter(ticket=ticket)
        serializer = TicketHistorySerializer(history, many=True)
        return Response(serializer.data)
    except Ticket.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def assign_ticket_to_operator(request, ticket_id, operator_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        operator = Operator.objects.get(id=operator_id)
        ticket.operator = operator
        ticket.save()
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)
    except (Ticket.DoesNotExist, Operator.DoesNotExist):
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def delay_ticket_service(request, ticket_id, delay_minutes):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        delay_time = timedelta(minutes=delay_minutes)
        ticket.service_time += delay_time
        ticket.save()
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)
    except Ticket.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def calculate_predicted_waiting_time(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        queue_length = int(request.GET.get('queue_length', 0))

        waiting_tickets = Ticket.objects.filter(queue=queue, status='waiting').exclude(wait_time=None)

        if waiting_tickets.exists():
            total_waiting_time = sum(ticket.wait_time.total_seconds() for ticket in waiting_tickets)
            average_waiting_time = total_waiting_time / len(waiting_tickets)
            predicted_waiting_time = timedelta(seconds=average_waiting_time * queue_length)
        else:
            predicted_waiting_time = timedelta(seconds=0)

        return Response({'predicted_waiting_time': predicted_waiting_time.total_seconds()})
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

User = get_user_model()

@api_view(['PUT'])
def update_customer_info(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.customer_name = request.data.get('customer_name')
        ticket.contact_info = request.data.get('contact_info')

        client_id = request.data.get('client_id')
        if client_id:
            try:
                client = User.objects.get(id=client_id)
                if isinstance(client, Client):
                    client.phone_number = request.data.get('phone_number')
                    client.address = request.data.get('address')
                    client.save()
                    ticket.client = client
                else:
                    return Response({'error': 'Invalid client ID'}, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({'error': 'Invalid client ID'}, status=status.HTTP_400_BAD_REQUEST)

        ticket.save()
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def pause_queue(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        queue.is_paused = True
        queue.save()
        serializer = QueueSerializer(queue)
        return Response(serializer.data)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def resume_queue(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        queue.is_paused = False
        queue.save()
        serializer = QueueSerializer(queue)
        return Response(serializer.data)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_most_loaded_queues(request):
    queues = Queue.objects.annotate(ticket_count=Count('ticket')).order_by('-ticket_count')
    data = []
    for queue in queues:
        ticket_count = Ticket.objects.filter(queue=queue).count()
        queue_data = {
            'id': queue.id,
            'name': queue.name,
            'created_at': queue.created_at,
            'queue_type': queue.queue_type,
            'priority': queue.priority,
            'queue_length': ticket_count,
            'standard_service_time': queue.standard_service_time,
            'priority_service_time': queue.priority_service_time,
            'vip_service_time': queue.vip_service_time,
            'max_limit': queue.max_limit,
            'is_paused': queue.is_paused,
            'branch': queue.branch.id,
        }
        data.append(queue_data)
    return Response(data)

@api_view(['GET'])
def get_least_loaded_queues(request):
    queues = Queue.objects.annotate(ticket_count=Count('ticket')).order_by('ticket_count')
    data = []
    for queue in queues:
        ticket_count = Ticket.objects.filter(queue=queue).count()
        queue_data = {
            'id': queue.id,
            'name': queue.name,
            'created_at': queue.created_at,
            'queue_type': queue.queue_type,
            'priority': queue.priority,
            'queue_length': ticket_count,
            'standard_service_time': queue.standard_service_time,
            'priority_service_time': queue.priority_service_time,
            'vip_service_time': queue.vip_service_time,
            'max_limit': queue.max_limit,
            'is_paused': queue.is_paused,
            'branch': queue.branch.id,
        }
        data.append(queue_data)
    return Response(data)


@api_view(['PUT'])
def set_max_waiting_time(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        max_waiting_time = request.data.get('max_waiting_time')
        queue.max_waiting_time = max_waiting_time
        queue.save()
        serializer = QueueSerializer(queue)
        return Response(serializer.data)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def change_ticket_priority(request, ticket_id, new_priority):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.priority = new_priority
        ticket.save()
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)
    except Ticket.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_current_waiting_time(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)
        current_waiting_time = queue.calculate_current_waiting_time()  # Метод для расчета текущего времени ожидания
        return Response({'current_waiting_time': current_waiting_time})
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def send_sms_notification(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        recipient_phone = ticket.user.phone_number
        message = f'Your ticket {ticket.ticket_number} status has been changed to {ticket.status}'

        # Настройки Twilio
        account_sid = 'your_account_sid'
        auth_token = 'your_auth_token'
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=message,
            from_='your_twilio_phone_number',
            to=recipient_phone
        )

        return Response({'message': 'Notification sent'})
    except Ticket.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def generate_ticket_send_mail(request, queue_id):
    try:
        queue = Queue.objects.get(id=queue_id)

        if queue.is_paused:
            return Response({'message': 'Cannot generate ticket. Queue is paused.'}, status=status.HTTP_400_BAD_REQUEST)

        # Получение клиента
        client_email = request.data.get('client_email')
        if not client_email:
            return Response({'message': 'Client email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = Client.objects.get(email=client_email)
        except Client.DoesNotExist:
            return Response({'message': 'Client not found.'}, status=status.HTTP_404_NOT_FOUND)

        ticket_number = generate_ticket_number()
        expiration_time = datetime.now() + timedelta(minutes=30)  # Истечение через 30 минут



        wait_time = None  # Инициализация времени ожидания



        # Расчет времени ожидания в зависимости от текущего состояния очереди и логики вашего приложения
        # wait_time = ...

        ticket = Ticket.objects.create(
            queue=queue,
            branch=queue.branch,
            ticket_number=ticket_number,
            created_at=datetime.now(),
            expiration_time=expiration_time,
            status='waiting',
            wait_time=wait_time,  # Присваивание времени ожидания
            client=client,  # Присваивание клиента талону
        )
        serializer = TicketSerializer(ticket)

        # Создание записи в истории билета
        history = TicketHistory.objects.create(ticket=ticket, action='Generated', timestamp=datetime.now())

        # Отправка номера талона клиенту
        send_notification_email.delay(client.email, ticket.ticket_number)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def call_ticket_to_operator(request, ticket_id, operator_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        operator = Operator.objects.get(id=operator_id)

        # Проверяем, свободен ли оператор
        if not operator.is_available:
            return Response({'message': 'Operator is not available'}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, принадлежит ли билет к очереди оператора
        if ticket.queue.branch != operator.branch:
            return Response({'message': 'Ticket does not belong to operator\'s branch'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, находится ли билет в ожидании
        if ticket.status != 'waiting':
            return Response({'message': 'Ticket is not in waiting status'}, status=status.HTTP_400_BAD_REQUEST)

        # Вызываем билет к оператору
        ticket.status = 'called'
        ticket.operator = operator
        ticket.save()

        serializer = TicketSerializer(ticket)
        return Response(serializer.data)

    except (Ticket.DoesNotExist, Operator.DoesNotExist):
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def call_next_available_operator(request, queue_id):
    try:
        from apps.operators.models import Operator
        queue = Queue.objects.get(id=queue_id)
        next_ticket = Ticket.objects.filter(queue=queue, status='waiting').order_by('created_at').first()

        if next_ticket:
            operator = Operator.objects.filter(is_available=True).exclude(id__in=Ticket.objects.filter(status='called').values('operator')).first()

            if operator:
                next_ticket.status = 'called'
                next_ticket.operator = operator
                next_ticket.save()

                serializer = TicketSerializer(next_ticket)
                return Response(serializer.data)

            return Response({'message': 'All operators are currently busy'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'No more tickets in the queue'}, status=status.HTTP_404_NOT_FOUND)

    except Queue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_operators_status(request):
    from apps.queue.models import Ticket
    operators = Operator.objects.all()
    operator_data = []

    for operator in operators:
        current_ticket = Ticket.objects.filter(operator=operator, status='called').first()
        if current_ticket is not None:
            ticket_status = 'Serving ticket'
            ticket_number = current_ticket.ticket_number
        else:
            ticket_status = 'Available'
            ticket_number = None

        operator_info = {
            'operator_id': operator.id,
            'name': operator.name.username,
            'is_available': operator.is_available,
            'branch': operator.branch.name,
            'ticket_status': ticket_status,
            'ticket_number': ticket_number,
        }
        operator_data.append(operator_info)

    return Response(operator_data)
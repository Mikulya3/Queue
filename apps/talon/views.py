from loguru import logger
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Ticket, TicketHistory
from apps.operators.models import Operator
from .serializers import TicketSerializer, TicketHistorySerializer
from rest_framework.exceptions import NotFound
from django.http import HttpResponse
from apps.talon.tasks import call_customer
from rest_framework.views import APIView
from datetime import datetime
from django.db import transaction


class TicketListAPIView(generics.ListAPIView):
    serializer_class = TicketSerializer

    def get_queryset(self):
        queryset = Ticket.objects.filter(operator__isnull=True).order_by('created_at')
        if not queryset.exists():
            raise NotFound('Талонов в очереди нет.')
        return queryset

class TicketListOperatorsAPIView(generics.ListAPIView):
    serializer_class = TicketSerializer

    def get_queryset(self):
        queryset = Ticket.objects.filter(operator__isnull=False).order_by('created_at')
        if not queryset.exists():
            raise NotFound('Талонов в обслуживании нет.')
        return queryset


class CallTicketAPIView(generics.UpdateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def update(self, request, *args, **kwargs):
        operator_id = kwargs['operator_id']
        try:
            operator = Operator.objects.get(id=operator_id)
        except Operator.DoesNotExist:
            return Response("Оператор не найден", status=status.HTTP_404_NOT_FOUND)

        # Проверяем, обслуживает ли оператор уже талон
        if operator.ticket_set.exists():
            return Response("Оператор уже обслуживает талон", status=status.HTTP_400_BAD_REQUEST)

        try:
            ticket = Ticket.objects.filter(operator=None).order_by('created_at').first()
        except Ticket.DoesNotExist:
            return Response("Талоны в очереди отсутствуют", status=status.HTTP_404_NOT_FOUND)

        ticket.operator = operator
        ticket.save()

        serializer = self.get_serializer(ticket)
        return Response(serializer.data)

def call_ticket_view(request):
    # Вызов Celery-задачи для автоматического вызова талона
    call_customer.delay()

    return HttpResponse("Задача по вызову талона запущена.")

class TalonCreateAPIView(APIView):
    def post(self, request, format=None):
        # Создание нового талона с номером в формате 'X-123' (где X - буква, 123 - цифры)
        last_ticket = Ticket.objects.order_by('-number').first()
        last_number = int(last_ticket.number.split('-')[1]) if last_ticket else 0
        new_number = chr(ord('A') + last_number // 1000) + '-' + str(last_number + 1).zfill(3)
        serializer = TicketSerializer(data={'number': new_number, **request.data})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteTicketAPIView(generics.DestroyAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def destroy(self, request, *args, **kwargs):
        ticket_id = kwargs['ticket_id']
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            logger.warning(f"Ticket {ticket_id} not found")
            return Response("Талон не найден", status=status.HTTP_404_NOT_FOUND)

        if not ticket.operator:
            logger.warning(f"Ticket {ticket_id} is not being serviced")
            return Response("Талон не обслуживается", status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Создание дубликата талона
            duplicate_ticket = Ticket.objects.create(
                created_at=ticket.created_at,
            )

            # Сохранение записи в историю талона с связью на дубликат талона
            history_entry = TicketHistory(
                ticket=duplicate_ticket,
                status=TicketHistory.STATUS_COMPLETED,
                completed_at=datetime.now()
            )
            history_entry.save()

            ticket.delete()
            logger.info(f'Ticket {ticket_id} successfully deleted')

        return Response("Талон успешно завершен")

class TicketHistoryListAPIView(generics.ListAPIView):
    queryset = TicketHistory.objects.all()
    serializer_class = TicketHistorySerializer
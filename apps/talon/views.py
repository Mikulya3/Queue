from loguru import logger
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Ticket, OutherTalon, CallCustomerTask, TicketArchive
from apps.operators.models import Operator
from .serializers import TicketSerializer, OutherTalonSerializer, TicketUpdateSerializer, CallCustomerTaskSerializer
from rest_framework.exceptions import NotFound
from django.http import HttpResponse
from rest_framework.views import APIView
from datetime import datetime
from django.db import transaction
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Max
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist







class TicketListAPIView(generics.ListAPIView):
    serializer_class = TicketSerializer

    def get_queryset(self):
        queryset = Ticket.objects.filter(operator__isnull=True).order_by('created_at')
        if not queryset.exists():
            raise NotFound('Талонов в очереди нет.')

        now = timezone.now()
        for ticket in queryset:
            ticket.actual_waiting_time = now - ticket.created_at

        return queryset


class TicketUpdateAPIView(generics.UpdateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketUpdateSerializer
    lookup_field = 'pk'  # Поле для поиска экземпляра билета (по умолчанию 'pk')

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        instance = self.get_object()
        data = request.data


        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class TicketListOperatorsAPIView(generics.ListAPIView):
    serializer_class = TicketSerializer

    def get_queryset(self):
        queryset = Ticket.objects.filter(operator__isnull=False).order_by('created_at')
        if not queryset.exists():
            raise NotFound('Талонов в обслуживании нет.')
        return queryset


from django.db.models import F


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
            ticket = operator.ticket_set.first()
            if ticket.failed_attempts < 2:
                ticket.failed_attempts += 1
                ticket.save()
                return Response("Вызов посетителя неудачен. Попытка номер {}.".format(ticket.failed_attempts))

            with transaction.atomic():
                try:
                    # Проверяем наличие талона в TicketArchive
                    if TicketArchive.objects.filter(number=ticket.number).exists():
                        # Если талон уже существует в TicketArchive, удаляем текущий талон
                        ticket.delete()
                        return Response("Талон уже существует в архиве. Текущий талон удален.",
                                        status=status.HTTP_200_OK)
                    # Создаем запись в TicketArchive для сохранения информации о талоне
                    ticket_archive = TicketArchive.objects.create(
                        number=ticket.number,
                        operator=ticket.operator,
                        is_veteran=ticket.is_veteran,
                        failed_attempts=ticket.failed_attempts,
                        status="Не подошел",  # Устанавливаем статус "Не подошел"

                        # Добавьте другие поля, которые нужно сохранить
                    )

                    # Удаляем текущий талон
                    ticket.delete()

                    # Восстанавливаем талон из TicketArchive
                    restored_ticket = Ticket.objects.create(
                        number=ticket_archive.number,
                        operator=None,  # Устанавливаем оператора как None
                        is_veteran=ticket_archive.is_veteran,
                        failed_attempts=ticket_archive.failed_attempts,
                        status="В очередь",
                        status_signal=True# Устанавливаем статус "Не подошел"
                        # Восстановьте другие поля из TicketArchive
                    )

                    # Возвращаем восстановленный талон в очередь
                    restored_ticket.save()

                    return Response("Талон успешно сохранен, удален и восстановлен.", status=status.HTTP_200_OK)
                except Exception as e:
                    return Response("Ошибка при сохранении, удалении или восстановлении талона.",
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Перемещаем талон обратно в конец очереди
            ticket.operator = None
            ticket.failed_attempts = 0
            ticket.save()

            # Перезагружаем объект ticket из базы данных, чтобы получить его обновленные значения
            ticket.refresh_from_db()

            return Response("Талон успешно перемещен в конец очереди.")

        try:
            # Получаем первый талон в очереди с галочкой is_veteran=True
            ticket = Ticket.objects.filter(operator=None, is_veteran=True).order_by('created_at').first()

            # Если не найдено талона с галочкой is_veteran=True, получаем любой доступный талон
            if ticket is None:
                ticket = Ticket.objects.filter(operator=None).order_by('created_at').first()
                if ticket is None:
                    return Response("Талоны в очереди отсутствуют", status=status.HTTP_404_NOT_FOUND)

        except Ticket.DoesNotExist:
            return Response("Талоны в очереди отсутствуют", status=status.HTTP_404_NOT_FOUND)

        # Устанавливаем оператора для талона
        ticket.operator = operator
        ticket.failed_attempts = 0
        ticket.save()

        serializer = self.get_serializer(ticket)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        operator_id = kwargs['operator_id']
        try:
            operator = Operator.objects.get(id=operator_id)
        except Operator.DoesNotExist:
            return Response("Оператор не найден", status=status.HTTP_404_NOT_FOUND)

        if operator.ticket_set.exists():
            ticket = operator.ticket_set.first()

        with transaction.atomic():
            try:
                # Создаем запись в TicketArchive для сохранения информации о талоне
                ticket_archive = TicketArchive.objects.create(
                    number=ticket.number,
                    operator=ticket.operator,
                    is_veteran=ticket.is_veteran,
                    failed_attempts=ticket.failed_attempts,
                    status="Не подошел",  # Устанавливаем статус "Не подошел"

                    # Добавьте другие поля, которые нужно сохранить
                )

                # Удаляем текущий талон
                ticket.delete()

                # Восстанавливаем талон из TicketArchive
                restored_ticket = Ticket.objects.create(
                    number=ticket_archive.number,
                    operator=None,  # Устанавливаем оператора как None
                    is_veteran=ticket_archive.is_veteran,
                    failed_attempts=ticket_archive.failed_attempts,
                    status="В очередь",
                    status_signal=True  # Устанавливаем статус "Не подошел"
                    # Восстановьте другие поля из TicketArchive
                )

                # Возвращаем восстановленный талон в очередь
                restored_ticket.save()

                return Response("Талон успешно сохранен, удален и восстановлен.", status=status.HTTP_200_OK)
            except Exception as e:
                return Response("Ошибка при сохранении, удалении или восстановлении талона.",
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Устанавливаем оператора как None для талона и сохраняем его
        ticket.operator = None
        ticket.failed_attempts = 0
        ticket.save()

        # Перезагружаем объект ticket из базы данных, чтобы получить его обновленные значения
        ticket.refresh_from_db()

        return Response("Талон успешно переведен в очередь", status=status.HTTP_200_OK)





class TalonCreateAPIView(APIView):
    def post(self, request, format=None):
        # Создание нового талона с уникальным номером в формате 'X-123' (где X - буква, 123 - цифры)
        number_exists = True
        new_number = None
        while number_exists:
            new_number = generate_ticket_number()
            number_exists = Ticket.objects.filter(number=new_number).exists()

        serializer = TicketSerializer(data={'number': new_number, **request.data})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def generate_ticket_number():
    last_number = get_last_ticket_number()  # Получение последнего номера талона
    new_number = chr(ord('A') + last_number // 1000) + '-' + str((last_number % 1000) + 1).zfill(3)
    update_last_ticket_number(last_number + 1)  # Обновление последнего номера талона
    return new_number

last_ticket_number = 0

def get_last_ticket_number():
    try:
        with open('last_ticket_number.txt', 'r') as file:
            last_number = int(file.read())
    except FileNotFoundError:
        last_number = 0
        update_last_ticket_number(last_number)
    return last_number

def update_last_ticket_number(new_number):
    with open('last_ticket_number.txt', 'w') as file:
        file.write(str(new_number))

class ResetTalonNumberAPIView(APIView):
    def post(self, request, format=None):
        new_start_number = request.data.get('start_number', 1)
        update_last_ticket_number(new_start_number - 1)
        return Response({'message': 'Номера талонов были сброшены.'}, status=status.HTTP_200_OK)

class CompleteTrueTicketAPIView(generics.DestroyAPIView):
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

        operator = ticket.operator  # Получить оператора, связанного с талоном
        ticket.delete()

        outher_talon = OutherTalon(number=ticket.number, operator=operator)
        outher_talon.end_time = datetime.now()  # Установите текущее время как время окончания обслуживания
        outher_talon.created_at = ticket.created_at  # Присвоить значение created_at из объекта Ticket
        outher_talon.start_time = ticket.created_at  # Установите значение start_time из объекта Ticket
        outher_talon.is_completed = True
        outher_talon.save()



        return Response("Талон успешно завершен")


class CompleteFalseTicketAPIView(generics.DestroyAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def destroy(self, request, *args, **kwargs):
        ticket_id = kwargs['ticket_id']
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response("Талон не найден", status=status.HTTP_404_NOT_FOUND)

        if not ticket.operator:
            return Response("Талон не обслуживается", status=status.HTTP_400_BAD_REQUEST)

        operator = ticket.operator  # Получить оператора, связанного с талоном
        ticket.delete()

        outher_talon = OutherTalon(number=ticket.number, operator=operator)
        outher_talon.end_time = datetime.now()  # Установите текущее время как время окончания обслуживания
        outher_talon.created_at = ticket.created_at  # Присвоить значение created_at из объекта Ticket
        outher_talon.start_time = ticket.created_at  # Установите значение start_time из объекта Ticket
        outher_talon.is_completed = False
        outher_talon.save()



        ticket.delete()
        logger.info(f'Ticket {ticket_id} successfully deleted')


        return Response("Талон успешно завершен")


class OutherTalonListAPIView(APIView):
    def get(self, request):
        outher_talons = OutherTalon.objects.all()
        serializer = OutherTalonSerializer(outher_talons, many=True)
        return Response(serializer.data)


class CallCustomerTaskView(APIView):
    def get(self, request):
        task = CallCustomerTask.objects.first()
        serializer = CallCustomerTaskSerializer(task)
        return Response(serializer.data)

    def put(self, request):
        task = CallCustomerTask.objects.first()
        serializer = CallCustomerTaskSerializer(task, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import serializers
from apps.talon.models import Ticket, OutherTalon, CallCustomerTask, TicketArchive
from apps.operators.serializers import OperatorSerializer
import re
from django.utils import timezone


def validate_ticket_number(value):
    pattern = r'^[A-Z]-\d{3}$'
    if not re.match(pattern, value):
        raise serializers.ValidationError("Неверный формат номера.")
    return value


class TicketSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    operator = OperatorSerializer(required=False)
    number = serializers.CharField(validators=[validate_ticket_number])
    actual_waiting_time = serializers.SerializerMethodField()



    class Meta:
        model = Ticket
        fields = ['id', 'number', 'created_at', 'actual_waiting_time', 'status', 'operator', 'is_veteran']  # Включаем поле 'operator' в опцию 'fields'

    def get_status(self, obj):
        if obj.operator is not None:
            return 'Обслуживается'
        else:
            return 'В очереди'

    def get_operator(self, obj):
        if obj.operator is not None:
            operator = obj.operator
            return {
                'id': operator.id,
                'name': operator.name,
                'is_available': operator.is_available
            }
        else:
            return None

    def get_actual_waiting_time(self, ticket):
        now = timezone.now()
        return now - ticket.created_at



class TicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['is_veteran']




class OutherTalonSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = OutherTalon
        fields = ['id', 'number', 'start_time', 'operator', 'end_time', 'status', 'is_completed']

    def get_status(self, obj):
        if obj.operator is not None:
            return 'Обслужен'


class CallCustomerTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallCustomerTask
        fields = ('enabled',)


class TicketArchiveSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    operator = OperatorSerializer(required=False)
    number = serializers.CharField(validators=[validate_ticket_number])
    actual_waiting_time = serializers.SerializerMethodField()



    class Meta:
        model = TicketArchive
        fields = ['id', 'number', 'created_at', 'actual_waiting_time', 'status', 'operator', 'is_veteran', 'status_signal']  # Включаем поле 'operator' в опцию 'fields'

    def get_status(self, obj):
        if obj.operator is not None:
            return 'Обслуживается'
        else:
            return 'В очереди'

    def get_operator(self, obj):
        if obj.operator is not None:
            operator = obj.operator
            return {
                'id': operator.id,
                'name': operator.name,
                'is_available': operator.is_available
            }
        else:
            return None







from rest_framework import serializers
from apps.talon.models import Ticket, TicketHistory
from apps.operators.serializers import OperatorSerializer
import re


def validate_ticket_number(value):
    pattern = r'^[A-Z]-\d{3}$'
    if not re.match(pattern, value):
        raise serializers.ValidationError("Неверный формат номера.")
    return value


class TicketSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    operator = OperatorSerializer(required=False)
    number = serializers.CharField(validators=[validate_ticket_number])

    class Meta:
        model = Ticket
        fields = ['id', 'number', 'created_at', 'status', 'operator']  # Включаем поле 'operator' в опцию 'fields'

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

class TicketHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketHistory
        fields = '__all__'
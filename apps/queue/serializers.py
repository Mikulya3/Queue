from rest_framework import serializers
from apps.queue.models import Queue, Ticket, TicketHistory
from apps.operators.serializers import OperatorSerializer

class QueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    operator = OperatorSerializer()  # Добавление поля оператор
    class Meta:
        model = Ticket
        fields = '__all__'


class TicketHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketHistory
        fields = '__all__'

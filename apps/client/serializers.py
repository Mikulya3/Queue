from rest_framework import serializers
from apps.client.models import ReservedTicket, Client, Review
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Client
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    rating = serializers.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    class Meta:
        model = Review
        fields = '__all__'

class ReservedTicketSerializer(serializers.ModelSerializer):
    service_time = serializers.TimeField(format='%H:%M:%S')

    class Meta:
        model = ReservedTicket
        fields = '__all__'


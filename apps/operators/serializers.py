from rest_framework import serializers, status
from .models import Operator

class OperatorSerializer(serializers.ModelSerializer):


    class Meta:
        model = Operator
        fields = ('id', 'name', 'is_available', 'email', 'window_number', 'position')









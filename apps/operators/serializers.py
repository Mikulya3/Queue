from rest_framework import serializers, status
from apps.operators.models import Operator

class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = '__all__'









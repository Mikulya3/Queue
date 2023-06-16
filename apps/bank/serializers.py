from rest_framework import serializers
from .models import Bank, Branch

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ('id', 'name', 'address', 'contact_number', 'email', 'description')

class BankSerializer(serializers.ModelSerializer):
    branches = BranchSerializer(many=True, read_only=True)

    class Meta:
        model = Bank
        fields = ('id', 'name', 'address', 'contact_number', 'email', 'established_date', 'branches', 'branch_director_name', 'branch_director_name_number')
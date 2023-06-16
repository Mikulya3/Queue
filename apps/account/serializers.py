from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.account.tasks import send_confirmation_email, send_confirmation_code

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    POSITION_CHOICES = (
        ('administrator', 'Administrator'),
        ('operator', 'Operator')
    )
    password_confirm = serializers.CharField(min_length=5, required=True, write_only=True)
    last_name = serializers.CharField(max_length=150, required=True, allow_blank=False)
    first_name = serializers.CharField(max_length=150, required=True, allow_blank=False)
    email = serializers.EmailField(max_length=254, required=True)
    password = serializers.CharField(max_length=128, required=True, allow_blank=False)
    username = serializers.CharField(required=True)
    position = serializers.ChoiceField(choices=POSITION_CHOICES)
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email', 'password', 'password_confirm','username','position','window_number']

    def validate(self, attrs):
        p1 = attrs.get('password')
        p2 = attrs.pop('password_confirm')

        if p1 != p2:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        code = user.activation_code
        send_confirmation_email(user.email, code)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    new_password_confirm = serializers.CharField(required=True, min_length=6)

    def validate(self, attrs):
        p1 = attrs.get('new_password')
        p2 = attrs.get('new_password_confirm')
        if p1 != p2:
            raise serializers.ValidationError('passwords are not match')
        return attrs

    def validate_old_password(self, p):
        request = self.context.get('request')
        user = request.user
        if not user.check_password(p):
            raise serializers.ValidationError('wrong password')
        return p

    def create(self, validated_data):
        user = self.context.get('request').user
        user.set_password(validated_data['new_password'])
        user.save(update_fields=['password'])
        return user

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    def validate_email(self,email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('user not exist!')
        return email
    def send_code(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.create_activation_code()
        user.save()
        send_confirmation_code(email, user.activation_code)


class ForgotPasswordCompleteSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)
    password = serializers.CharField(required=True, min_length=6)
    password_confirm = serializers.CharField(required=True,min_length=6)
    def validate_email(self,email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('user not register')
        return email

    def validate_code(self, code):
        if not User.objects.filter(activation_code = code).exists():
            raise serializers.ValidationError('wrong code!')
        return code
    def validate(self,attrs):
        p1 = attrs.get('password')
        p2 = attrs.get('password_confirm')
        if p1 != p2 :
            raise serializers.ValidationError('passwords are not match!')
        return attrs
    def set_new_password(self):
        email = self.validated_data.get('email')
        password = self.validated_data.get('password')
        user = User.objects.get(email=email)
        user.set_password(password)
        user.activation_code = ''
        user.save()
        return password


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=5, write_only=True)




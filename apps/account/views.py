from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.account.serializers import RegisterSerializer, ChangePasswordSerializer, DeleteAccountSerializer, \
    ForgotPasswordSerializer, ForgotPasswordCompleteSerializer

User = get_user_model()


class RegisterAPIView(APIView):
    POSITION_CHOICES = (
        ('admin', 'Administrator'),
        ('operator', 'Operator')
    )
    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            'You have successfully registered.'
            'An activation email has been sent to you',
            status=status.HTTP_201_CREATED
        )

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response('Password changed successfully', status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordAPIView(APIView):
    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.send_code()
        return Response('we have sent you letter to recovery your password!')


class ForgotPasswordCompleteAPIView(APIView):
    @swagger_auto_schema(request_body=ForgotPasswordCompleteSerializer)
    def post(self, request):
        serializer = ForgotPasswordCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.set_new_password()
        return Response('password have successfully changed!')

class ActivationApiView(APIView):
    @staticmethod
    def get(request, activation_code):
        try:
            user = User.objects.get(activation_code=activation_code)
            user.is_active = True
            user.activation_code = ''
            user.save()
            return Response({'message': 'успешно'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)

class DeleteAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=DeleteAccountSerializer)
    def post(self, request):
        password = request.data.get('password')
        if not request.user.check_password(password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.delete()
        return Response({'message': 'Account deleted successfully'}, status=status.HTTP_200_OK)




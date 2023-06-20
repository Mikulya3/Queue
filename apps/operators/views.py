from loguru import logger
from rest_framework import status
from rest_framework.views import APIView
from apps.operators.models import Operator
from apps.queue.serializers import OperatorSerializer
from rest_framework.response import Response
from rest_framework import generics
logger.add("file_{time}.log", level="TRACE", rotation="100 MB")

# Выводит по запросу список всех операторов --------------------------------------------------------------------------->
class OperatorListAPIView(APIView):
    def get(self, request, format=None):
        operators = Operator.objects.all()
        serializer = OperatorSerializer(operators, many=True)
        response_data = {
            'message': 'Список всех операторов',
            'operators': serializer.data
        }
        return Response(response_data)

# ---------------------------------------------------------------------------------------------------------------------<

# Создает оператора, ссылаясь на данные из id - account и выдает персональный id - оператора -------------------------->
# Принимает 2 поля Обязательно: name(int); Необязательно: is_available(bool - принимает по умолчанию true)

class OperatorCreateView(APIView):
    @logger.catch()
    def post(self, request, format=None):
        serializer = OperatorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Оператор успешно создан"}, status=status.HTTP_201_CREATED)
        print(serializer.errors)  # Debugging: Print serializer errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------------------------------------------------<

# Обновляет параметры оператора, выставляет is_available на true либо false  ------------------------------------------>
# Принимает 2 поля Обязательно: name(int); Необязательно: is_available(bool)
class OperatorUpdateView(generics.UpdateAPIView):
    serializer_class = OperatorSerializer
    queryset = Operator.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = {
            'message': 'Оператор успешно обновлен',
            'data': serializer.data
        }
        return Response(data)

# ---------------------------------------------------------------------------------------------------------------------<

# Удаляет оператора, принимает в запросе /pk/ ------------------------------------------------------------------------->

class OperatorDeleteView(generics.DestroyAPIView):
    serializer_class = OperatorSerializer
    queryset = Operator.objects.all()

    @logger.catch()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Оператор успешно удален", "data": self.get_serializer(instance).data})

# ---------------------------------------------------------------------------------------------------------------------<





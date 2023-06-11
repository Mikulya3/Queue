from django.urls import path
from apps.operators.views import OperatorListAPIView, OperatorCreateView, OperatorUpdateView, OperatorDeleteView
#from apps.operators.views import OperatorCreateView

urlpatterns = [
    # Другие URL-маршруты вашего приложения
    path('operator_list/', OperatorListAPIView.as_view(), name='operator-create'),
    path('create/', OperatorCreateView.as_view(), name='operator-create'),
    path('<int:pk>/', OperatorUpdateView.as_view(), name='operator-update'),
    path('<int:pk>/delete/', OperatorDeleteView.as_view(), name='operator-delete'),
]
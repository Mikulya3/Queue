from django.urls import path
from apps.talon.views import TicketListAPIView, TicketListOperatorsAPIView, CallTicketAPIView, TalonCreateAPIView, \
    CompleteTrueTicketAPIView, CompleteFalseTicketAPIView, OutherTalonListAPIView, TicketUpdateAPIView, ResetTalonNumberAPIView, CallCustomerTaskView





urlpatterns = [
    # Другие URL-маршруты вашего проекта
    path('queue/', TicketListAPIView.as_view(), name='queue'),
    path('queueoperators/', TicketListOperatorsAPIView.as_view(), name='queue'),
    path('operators/<int:operator_id>/call-ticket/', CallTicketAPIView.as_view(), name='call-ticket'),
    path('operators/<int:pk>/<int:operator_id>/', CallTicketAPIView.as_view(), name='call-ticket-number-operator'),
    path('create/', TalonCreateAPIView.as_view(), name='talon_create'),
    path('talon/reset/', ResetTalonNumberAPIView.as_view(), name='reset_talon_number'),
    path('completeTrue/<int:ticket_id>/', CompleteTrueTicketAPIView.as_view(), name='talon-complete'),
    path('completeFalse/<int:ticket_id>/', CompleteFalseTicketAPIView.as_view(), name='talon-complete'),
    path('outher-talons/', OutherTalonListAPIView.as_view(), name='outher-talon-list'),
    path('tickets/<int:pk>/update/', TicketUpdateAPIView.as_view(), name='ticket_update'),
    path('call-customer-task/', CallCustomerTaskView.as_view(), name='call-customer-task'),


]
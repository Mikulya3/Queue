from django.urls import path
from apps.talon.views import TicketListAPIView, TicketListOperatorsAPIView, CallTicketAPIView, call_ticket_view, TalonCreateAPIView, \
    CompleteTicketAPIView, TicketHistoryListAPIView




urlpatterns = [
    # Другие URL-маршруты вашего проекта
    path('queue/', TicketListAPIView.as_view(), name='queue'),
    path('queueoperators/', TicketListOperatorsAPIView.as_view(), name='queue'),
    path('operators/<int:operator_id>/call-ticket/', CallTicketAPIView.as_view(), name='call-ticket'),
    path('operators/<int:ticket_number>/<int:operator_id>/', CallTicketAPIView.as_view(), name='call-ticket-number-operator'),
    path('call-ticket/', call_ticket_view, name='call_ticket'),
    path('create/', TalonCreateAPIView.as_view(), name='talon_create'),
    path('complete/<int:ticket_id>/', CompleteTicketAPIView.as_view(), name='talon-complete'),
    path('ticket-history/', TicketHistoryListAPIView.as_view(), name='ticket-history'),

]
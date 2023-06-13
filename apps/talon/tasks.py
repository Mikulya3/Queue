from celery import shared_task
from apps.talon.models import Ticket
from apps.operators.models import Operator
from apps.talon.models import CallCustomerTask  # Импортируйте класс CallCustomerTask


@shared_task
def call_customer():
    task = CallCustomerTask.objects.first()

    if not task.enabled:
        return

    operators = Operator.objects.filter(is_available=True)

    for operator in operators:
        if operator.ticket_set.exists():
            # Оператор уже обслуживает талон
            continue

        try:
            ticket = Ticket.objects.filter(operator=None).order_by('created_at').first()
        except Ticket.DoesNotExist:
            # Талоны в очереди отсутствуют
            break

        ticket.operator = operator
        ticket.save()

    # Используйте CallCustomerTask
    call_customer_task = CallCustomerTask.objects.first()
    if call_customer_task and not call_customer_task.enabled:
        # Задача отключена, прерываем выполнение
        return



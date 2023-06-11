from config.celery import app
from django.core.mail import send_mail
from decouple import config


@app.task
def send_confirmation_email(email, code):
    full_link = f'http://localhost:8000/accounts/activate/{code}'
    send_mail(
        'Активация пользователя',
        full_link,
        'kadirbekova43@gmail.com',
        [email]
    )

def send_confirmation_code(email, code):
    send_mail(
        'Восстановление пароля',
        code,
        'Kadirbekova43@gmail.com',
        [email]
    )




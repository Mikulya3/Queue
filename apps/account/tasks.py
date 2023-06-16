from decouple import config

from config.celery import app
from django.core.mail import send_mail

@app.task
def send_confirmation_email(email, code):
    full_link = f'http://localhost:8000/ru/account/activate/{code}'
    send_mail(
        'User activation',
        f'Пажалуйста подтвердите аккаунт перейдя по ссылке: {full_link}',
        config('EMAIL_HOST_USER'),
        [email]
    )

def send_confirmation_code(email, code):
    send_mail(
        'Восстановление пароля',
        code,
        config('EMAIL_HOST_USER'),
        [email]

    )



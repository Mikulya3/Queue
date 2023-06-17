"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from datetime import datetime, timedelta
from django.utils.translation import gettext_lazy as _
import dj_database_url
from decouple import config
from pathlib import Path

from loguru import logger

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!


ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')


DEBUG = config('DEBUG')



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
<<<<<<< HEAD
=======
    'corsheaders',
    'django_crontab',
>>>>>>> ab43b1fe5b8efee48a8f6060d4dfd240102951df

    # lib
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',
    'django_filters',
    'dj_database_url',
    'django_celery_beat',
    'corsheaders',

    # apps
    'apps.account',
    'apps.operators',
    'apps.talon',
    'apps.bank',
    'apps.equipment',
    'apps.queue',
    'apps.client',
    # 'apps.administrator'

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(default=config('DATABASE_URL')
    )
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'En-en'

LANGUAGES = (
    ('kg', _('Kirghiz')),
    ('en', _('English')),
    ('ru', _('Russian')),
)

TIME_ZONE = 'Asia/Bishkek'

USE_I18N = True
USE_L10N = True
USE_TZ = True



LOCALE_PATHS = [
   os.path.join(BASE_DIR, 'locale')
]



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

AUTH_USER_MODEL = 'account.QueueUser'
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=300),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',

]
CORS_ALLOW_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
    'https://www.thunderclient.com',
    'https://fullstackhackaton-e8324.web.app'
]

CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
    'https://www.thunderclient.com',
    'https://fullstackhackaton-e8324.web.app'
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')

BROKER_URL = 'redis://127.0.0.1:6379/0'


RESULT_BACKEND = 'redis://127.0.0.1:6379/0'  # URL для хранения результатов задач
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_BEAT_SCHEDULE = {
    'call_next_available_operator_auto_task': {
        'task': 'apps.queue.tasks.call_next_available_operator_auto_task',
        'schedule': timedelta(seconds=10),
    },
}


BROKER_TRANSPORT = 'redis'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IMPORTS = ('apps.account.tasks',)


SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    }
}


# создаем папку logs
log_directory = os.path.join(BASE_DIR, 'logs')
os.makedirs(log_directory, exist_ok=True)
rotation_duration = timedelta(days=15).total_seconds() # переводим 15 дней в сек
logger.add(                                            # настройки loguru
    os.path.join(log_directory, 'talon.log'),
    rotation=rotation_duration,
    retention='15 days',  # автоудаление после 15 дней
    level='DEBUG'  #
)


LOGGING = {
     'version': 1,
     'disable_existing_loggers': False,
     'formatters': {
         'config': {
             'format': '{levelname} --{asctime} -- {module} --{message}',
             'style': '{'
         }
     },
     'handlers': {
         'my_console': {
             'class': 'logging.StreamHandler',
             'formatter': 'config'
         },
         'file': {
             'class': 'logging.FileHandler',
             'filename': 'app.log',
             'formatter': 'config',
         },
         'for_registrator': {
             'class': 'logging.FileHandler',
             'filename': 'apps.registrator.log',
             'formatter': 'config',
         },
         'for_talon': {
             'class': 'logging.FileHandler',
             'filename': 'apps.talon.log',
             'formatter': 'config',
         },
     },
     'loggers': {
         '': {
             'handlers': ['my_console', 'file']
         },
         'apps.registrator.views': {
             'handlers': ['for_registrator']
         }
     }

 }



# Redis settings
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
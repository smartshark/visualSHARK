from .base import *

SECRET_KEY = None

DEBUG = True

ALLOWED_HOSTS = []

CORS_ORIGIN_WHITELIST = (
    '127.0.0.1',
    'localhost:8080',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'visualshark',
        'USER': '',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    'mongodb_local': {
        'ENGINE': '',
        'NAME': 'smartshark',
        'USER': '',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': 27017,
        'AUTHENTICATION_DB': 'smartshark',
        'SUPPORTS_TRANSACTIONS': False,
    },
    'mongodb': {
        'ENGINE': '',
        'NAME': 'smartshark_test',
        'USER': '',
        'PASSWORD': '',
        'HOST': '141.5.113.177',
        'PORT': 27017,
        'AUTHENTICATION_DB': 'smartshark_test',
        'SUPPORTS_TRANSACTIONS': False,
    }
}

DATABASE_ROUTERS = ['visualSHARK.routers.MongoRouter']

# rabbitmq settings for worker and sending messages
QUEUE = {
    'server': 'localhost',
    'port': '5672',
    'ssl': False,
    'user': 'guest',
    'password': 'guest',
    'vhost': '/',
    'job_queue': 'jobs'
}

# ServerSHARK API KEY
API_KEY = None
SERVERSHARK_API_URL = 'http://127.0.0.1:8001/remote'

from .base import *

SECRET_KEY = 'documentationonly'

DEBUG = True

ALLOWED_HOSTS = []

CORS_ORIGIN_WHITELIST = (
    '127.0.0.1',
    'localhost:8080',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'visualsharkdoc',
    },
    'mongodb': {
        'ENGINE': '',
        'NAME': 'smartshark',
        'USER': '',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': 27017,
        'AUTHENTICATION_DB': 'smartshark',
        'SUPPORTS_TRANSACTIONS': False,
    },
}

DATABASE_ROUTERS = ['visualSHARK.routers.MongoRouter']
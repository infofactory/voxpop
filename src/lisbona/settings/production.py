from .base import *

DEBUG = False

ALLOWED_HOSTS = ['open.willeasy.app', 'voxpop.infofactory.it', 'localhost']


# Database Postgresql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'voxpop',
        'USER': 'voxpop',
        'PASSWORD': 'Lì es bona!',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


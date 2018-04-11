import os
from anthill.common.conf.settings import *

# Build paths inside the application like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dsuy#yg2#h+0msm)lja9sz(xtb)*a81215z#uyj3$im0^d1m$t'

DEBUG = False

SQLALCHEMY_DATABASE_URI = 'postgres://ah_admin@/ah_admin'

ROUTES_CONF = 'admin.routes'

LOCATION = 'http://localhost:9500'
BROKER = 'amqp://guest:guest@localhost:5672'

APPLICATION_CLASS = 'admin.apps.AnthillApplication'
APPLICATION_NAME = 'admin'
APPLICATION_VERBOSE_NAME = 'Admin'
APPLICATION_DESCRIPTION = None
APPLICATION_ICON_CLASS = None

SERVICE_CLASS = 'admin.services.Service'

STATIC_PATH = os.path.join(BASE_DIR, 'ui', 'static')
TEMPLATE_PATH = os.path.join(BASE_DIR, 'ui', 'templates')

STATIC_URL = '/static/'

UI_MODULE = 'admin.ui'

CONTEXT_PROCESSORS = [
    'anthill.framework.handlers.context_processors.datetime',
    'admin.context_processors.main_sidebar'
]

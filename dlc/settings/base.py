import os
from anthill_platform.settings import *

# Build paths inside the application like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'DLC_SERVICE_SECRET_KEY'

DEBUG = False

SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@localhost/ah_dlc'

LOCATION = 'http://localhost:9505'
BROKER = 'amqp://guest:guest@localhost:5672'

ROUTES_CONF = 'dlc.routes'

APPLICATION_CLASS = 'dlc.apps.AnthillApplication'
APPLICATION_NAME = 'dlc'
APPLICATION_VERBOSE_NAME = 'DLC'
APPLICATION_DESCRIPTION = 'Deliver downloadable content to a user'
APPLICATION_ICON_CLASS = None

SERVICE_CLASS = 'dlc.services.Service'

STATIC_PATH = os.path.join(BASE_DIR, 'ui', 'static')
TEMPLATE_PATH = os.path.join(BASE_DIR, 'ui', 'templates')

STATIC_URL = '/static/'

UI_MODULE = 'dlc.ui'

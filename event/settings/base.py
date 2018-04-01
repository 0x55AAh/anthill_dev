import os
from anthill_platform.settings import *

# Build paths inside the application like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'EVENT_SERVICE_SECRET_KEY'

DEBUG = False

SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@localhost/ah_event'

LOCATION = 'http://localhost:9506'
BROKER = 'amqp://guest:guest@localhost:5672'

ROUTES_CONF = 'event.routes'

APPLICATION_CLASS = 'event.apps.AnthillApplication'
APPLICATION_NAME = 'event'
APPLICATION_VERBOSE_NAME = 'Event'
APPLICATION_DESCRIPTION = 'Compete players with time-limited events'
APPLICATION_ICON_CLASS = None

SERVICE_CLASS = 'event.services.Service'

STATIC_PATH = os.path.join(BASE_DIR, 'ui', 'static')
TEMPLATE_PATH = os.path.join(BASE_DIR, 'ui', 'templates')

STATIC_URL = '/static/'

UI_MODULE = 'event.ui'
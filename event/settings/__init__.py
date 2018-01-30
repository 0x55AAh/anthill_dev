import os

# Build paths inside the application like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'EVENT_SERVICE_SECRET_KEY'

DEBUG = False

DATABASES = {
    'default': {
        'url': 'postgres://user:pass@localhost/ah_event',
        'encoding': 'utf-8'
    }
}

LOCATION = 'http://localhost:9506'
BROKER = 'amqp://guest:guest@localhost:5672'

ROUTES_CONF = 'event.routes'

APPLICATION_CLASS = 'event.apps.AnthillApplication'
APPLICATION_NAME = 'event'
APPLICATION_VERBOSE_NAME = 'Event'
APPLICATION_DESCRIPTION = 'Compete players with time-limited events'
APPLICATION_ICON_CLASS = None

SERVICE_CLASS = 'event.services.Service'

try:
    from anthill_platform.settings import *
except ImportError:
    pass

try:
    from .local import *
except ImportError:
    pass

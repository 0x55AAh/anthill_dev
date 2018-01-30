import os

# Build paths inside the application like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'DLC_SERVICE_SECRET_KEY'

DEBUG = False

DATABASES = {
    'default': {
        'url': 'postgres://user:pass@localhost/ah_dlc',
        'encoding': 'utf-8'
    }
}

LOCATION = 'http://localhost:9505'
BROKER = 'amqp://guest:guest@localhost:5672'

ROUTES_CONF = 'dlc.routes'

APPLICATION_CLASS = 'dlc.apps.AnthillApplication'
APPLICATION_NAME = 'dlc'
APPLICATION_VERBOSE_NAME = 'DLC'
APPLICATION_DESCRIPTION = 'Deliver downloadable content to a user'
APPLICATION_ICON_CLASS = None

SERVICE_CLASS = 'dlc.services.Service'

try:
    from anthill_platform.settings import *
except ImportError:
    pass

try:
    from .local import *
except ImportError:
    pass

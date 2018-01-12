# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1234'

DEBUG = False

REGISTERED_SERVICES = {
    'admin': {
        'internal': 'http://localhost:9500',
        'external': 'http://localhost:9500',
        'broker': 'amqp://guest:guest@localhost:5672'
    },
    'discovery': {
        'internal': 'http://localhost:9502',
        'external': 'http://localhost:9502',
        'broker': 'amqp://guest:guest@localhost:5672'
    },
    'dlc': {
        'internal': 'http://localhost:9505',
        'external': 'http://localhost:9505',
        'broker': 'amqp://guest:guest@localhost:5672'
    },
    'event': {
        'internal': 'http://localhost:9506',
        'external': 'http://localhost:9506',
        'broker': 'amqp://guest:guest@localhost:5672'
    },
}

DATABASES = {
    'default': {
        'url': 'postgres://user:pass@localhost/ah_discovery',
        'encoding': 'utf-8'
    }
}

LOCATION = 'http://localhost:9502'

ROUTES_CONF = 'discovery.routes'

APPLICATION_CLASS = 'discovery.apps.AnthillApplication'
APPLICATION_NAME = 'discovery'
APPLICATION_VERBOSE_NAME = 'Discovery'
APPLICATION_DESCRIPTION = 'Map each service location dynamically'
APPLICATION_ICON_CLASS = None

SERVICE_CLASS = 'discovery.services.Service'

try:
    from anthill_platform.settings import *
except ImportError:
    pass

try:
    from .local import *
except ImportError:
    pass

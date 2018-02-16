import os
from anthill_platform.settings import *

# Build paths inside the application like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'DISCOVERY_SERVICE_SECRET_KEY'

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

REGISTERED_SERVICES_EXTERNAL = os.path.join(BASE_DIR, 'registry.json')

SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@localhost/ah_discovery'

LOCATION = 'http://localhost:9502'
BROKER = 'amqp://guest:guest@localhost:5672'

ROUTES_CONF = 'discovery.routes'

APPLICATION_CLASS = 'discovery.apps.AnthillApplication'
APPLICATION_NAME = 'discovery'
APPLICATION_VERBOSE_NAME = 'Discovery'
APPLICATION_DESCRIPTION = 'Map each service location dynamically'
APPLICATION_ICON_CLASS = None

SERVICE_CLASS = 'discovery.services.Service'

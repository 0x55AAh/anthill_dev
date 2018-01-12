# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1234'

DEBUG = False

DATABASES = {
    'default': {
        'url': 'postgres://user:pass@localhost/ah_event',
        'encoding': 'utf-8'
    }
}

LOCATION = 'http://localhost:9506'

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

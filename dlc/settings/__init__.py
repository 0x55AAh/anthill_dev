# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1234'

DEBUG = False

DATABASES = {
    'default': {
        'url': 'postgres://user:pass@localhost/ah_dlc',
        'encoding': 'utf-8'
    }
}

LOCATION = 'http://localhost:9505'

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

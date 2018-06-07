import os
from anthill.platform.conf.settings import *

# Build paths inside the application like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '09m0q%d0d1l*1y@4awc&y@z&3*5#v!=-yvmx^+eoa2so33t_55'

DEBUG = False

ADMINS = (
    ('Lysenko Vladimir', 'wofkin@gmail.com'),
)

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
APPLICATION_ICON_CLASS = 'icon-direction'
APPLICATION_COLOR = 'danger'

SERVICE_CLASS = 'discovery.services.Service'

STATIC_PATH = os.path.join(BASE_DIR, 'ui', 'static')
TEMPLATE_PATH = os.path.join(BASE_DIR, 'ui', 'templates')

STATIC_URL = '/static/'

UI_MODULE = 'discovery.ui'

CACHES["default"]["LOCATION"] = "redis://localhost:6379/3"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'anthill.framework.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'anthill.framework.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'anthill.server': {
            '()': 'anthill.framework.utils.log.ServerFormatter',
            'fmt': '%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'color': False,
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'anthill.server',
        },
        'anthill': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '../discovery.log',
            'formatter': 'anthill.server',
            'maxBytes': 100 * 1024 * 1024,
            'backupCount': 10
        },
        'anthill.server': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '../discovery.log',
            'formatter': 'anthill.server',
            'maxBytes': 100 * 1024 * 1024,
            'backupCount': 10
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'anthill.framework.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'anthill': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': False
        },
        'anthill.application': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'anthill.server': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'tornado.access': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'tornado.application': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'tornado.general': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'celery': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'celery.worker': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'celery.task': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
        'celery.redirected': {
            'handlers': ['anthill.server'],
            'level': 'INFO',
            'propagate': False
        },
    }
}


#########
# GEOIP #
#########

GEOIP_PATH = os.path.join(BASE_DIR, '../')


#########
# HTTPS #
#########

# HTTPS = {
#     'key_file': os.path.join(BASE_DIR, '../server.key'),
#     'crt_file': os.path.join(BASE_DIR, '../server.crt'),
# }
HTTPS = None


############
# GRAPHENE #
############

GRAPHENE = {
    'SCHEMA': 'discovery.api.v1.public.schema',
    'MIDDLEWARE': ()
}

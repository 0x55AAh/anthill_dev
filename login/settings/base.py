import os
from anthill.platform.conf.settings import *

# Build paths inside the application like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+^a$ohe7j=fvitfyh__77m_24cc5zw1@9j9lhe@-*e)&amp;-m5zv3'

DEBUG = False

ADMINS = (
    ('Lysenko Vladimir', 'wofkin@gmail.com'),
)

SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@localhost/ah_login'

LOCATION = 'http://localhost:9507'
BROKER = 'amqp://guest:guest@localhost:5672'

ROUTES_CONF = 'login.routes'

STATIC_PATH = os.path.join(BASE_DIR, 'ui', 'static')
TEMPLATE_PATH = os.path.join(BASE_DIR, 'ui', 'templates')

APPLICATION_CLASS = 'login.apps.AnthillApplication'
APPLICATION_NAME = 'login'
APPLICATION_VERBOSE_NAME = 'Login'
APPLICATION_DESCRIPTION = 'Manage user accounts, credentials and access tokens'
APPLICATION_ICON_CLASS = 'icon-key'
APPLICATION_COLOR = 'pink'

SERVICE_CLASS = 'login.services.Service'

STATIC_URL = '/static/'

UI_MODULE = 'login.ui'

CONTEXT_PROCESSORS = [

]

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
            'filename': '../login.log',
            'formatter': 'anthill.server',
            'maxBytes': 100 * 1000 * 1000,
            'backupCount': 10
        },
        'anthill.server': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '../login.log',
            'formatter': 'anthill.server',
            'maxBytes': 100 * 1000 * 1000,
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
    'SCHEMA': 'login.api.v1.public.schema',
    'MIDDLEWARE': ()
}

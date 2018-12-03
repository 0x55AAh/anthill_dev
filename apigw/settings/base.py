import os
from anthill.framework.utils.translation import translate_lazy as _
from anthill.platform.conf.settings import *

# Build paths inside the application like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'po)j0fl)#v6-z4#ymyhw00_4bx2k)&amp;@(jn1(-k180%r)6x=o62'

DEBUG = False

ADMINS = (
    ('Lysenko Vladimir', 'wofkin@gmail.com'),
)

SQLALCHEMY_DATABASE_URI = 'postgres://anthill_apigw@/anthill_apigw'

LOCATION = 'http://localhost:9516'
BROKER = 'amqp://guest:guest@localhost:5672'

# ROUTES_CONF = 'apigw.routes'

STATIC_PATH = os.path.join(BASE_DIR, 'ui', 'static')
TEMPLATE_PATH = os.path.join(BASE_DIR, 'ui', 'templates')
LOCALE_PATH = os.path.join(BASE_DIR, 'locale')

# APPLICATION_CLASS = 'apigw.apps.AnthillApplication'
APPLICATION_NAME = 'apigw'
APPLICATION_VERBOSE_NAME = _('API')
APPLICATION_DESCRIPTION = _('Api gateway service')
APPLICATION_ICON_CLASS = 'icon-puzzle'
APPLICATION_COLOR = 'purple'

# SERVICE_CLASS = 'apigw.services.Service'

STATIC_URL = '/static/'

# UI_MODULE = 'apigw.ui'

EMAIL_SUBJECT_PREFIX = '[Anthill: apigw] '

CACHES["default"]["LOCATION"] = "redis://localhost:6379/26"

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
        'anthill.server': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/anthill/apigw.log',
            'formatter': 'anthill.server',
            'maxBytes': 100 * 1024 * 1024,  # 100 MiB
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
        },
        'anthill.application': {
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
        'asyncio': {
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


PUBLIC_API_URL = '/api/'


############
# GRAPHENE #
############

GRAPHENE = {
    'SCHEMA': 'apigw.api.v1.public.schema',
    'MIDDLEWARE': ()
}

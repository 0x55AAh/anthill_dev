from anthill.framework.utils.translation import translate_lazy as _
from anthill.platform.conf.settings import *
import os

# Build paths inside the application like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nrc_!b1_n4!7cx!4!^&amp;hfu^5axl3_fhki)rbyavnh@mthrk@op'

DEBUG = False

ADMINS = (
    ('Lysenko Vladimir', 'wofkin@gmail.com'),
)

SQLALCHEMY_DATABASE_URI = 'postgres://anthill_media@/anthill_media'

LOCATION = 'http://localhost:9615'
BROKER = 'amqp://guest:guest@localhost:5672'

# ROUTES_CONF = 'media.routes'

LOCALE_PATH = os.path.join(BASE_DIR, 'locale')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# APPLICATION_CLASS = 'media.apps.AnthillApplication'
APPLICATION_NAME = 'media'
APPLICATION_VERBOSE_NAME = _('Media')
APPLICATION_DESCRIPTION = _('Manage user uploaded files')
APPLICATION_ICON_CLASS = 'icon-file-media'
APPLICATION_COLOR = 'teal'

# SERVICE_CLASS = 'media.services.Service'

CACHES["default"]["LOCATION"] = "redis://localhost:6379/25"
CACHES["default"]["KEY_PREFIX"] = "media.anthill"

EMAIL_SUBJECT_PREFIX = '[Anthill: media] '

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
            'filename': os.path.join(LOGGING_ROOT_DIR, 'media.log'),
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

############
# GRAPHENE #
############

GRAPHENE = {
    'SCHEMA': 'media.api.v1.public.schema',
    'MIDDLEWARE': ()
}

#############
# THUMBNAIL #
#############

THUMBNAIL_DEFAULT_OPTIONS = {
    'resize': 'fill',  # 'fill', 'fit', 'stretch'
    'upscale': True,
    'format': None,  # 'JPEG', 'PNG'
    'quality': 90,
    'progressive': True,
    'orientation': True,
    'optimize': False,
}
THUMBNAIL_ALIASES = {
    'test': {
        'geometry': '250x250',
        'filters': [('crop', '250x250', 'center', 'center')],
        'options': {'optimize': True, 'quality': 90, 'format': 'PNG'}
    }
}
THUMBNAIL_DIR = 'thumbs'

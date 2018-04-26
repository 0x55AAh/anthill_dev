NETWORKS = ['internal', 'external']

EMAIL_SUBJECT_PREFIX = '[Anthill] '

RESOLVERS = {
    "default": {
        'internal': 'http://localhost:9502',
        'external': 'http://localhost:9502',
        'broker': 'amqp://guest:guest@localhost:5672'
    }
}

DISCOVERY_SECRET_KEY = 'DISCOVERY_SERVICE_SECRET_KEY'

CACHES = {
    "default": {
        "BACKEND": "anthill.framework.core.cache.backends.redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "anthill.framework.core.cache.backends.redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 500
            }
        }
    }
}
REDIS_IGNORE_EXCEPTIONS = False
REDIS_LOG_IGNORED_EXCEPTIONS = False
REDIS_LOGGER = False
REDIS_SCAN_ITERSIZE = 10


##########
# CELERY #
##########

CELERY_LOG_LEVEL = 'info'

# All celery configuration options:
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#configuration
CELERY_SETTINGS = {
    'broker_url': 'amqp://guest:guest@localhost:5672',
    'result_backend': 'redis://'
}

CELERY_APP_NAME = 'tasks'

CELERY_ENABLE = False


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'anthill.framework.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'anthill.framework.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'anthill.framework.auth.password_validation.NumericPasswordValidator',
    },
]

CSRF_COOKIES = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'anthill.server': {
            '()': 'anthill.framework.utils.log.ServerFormatter',
            'fmt': '%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '%',
        }
    },
    'handlers': {
        'anthill': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'anthill.server',
        },
        'anthill.server': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'anthill.server',
        },
    },
    'loggers': {
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


##############
# RATE LIMIT #
##############

RATE_LIMIT_ENABLE = False
RATE_LIMIT_CACHE_PREFIX = 'rl:'

RATE_LIMIT_CONFIG = {
    'resource1': {'rate': '15/s'},
    'resource2': {'rate': '8/m'},
    'resource3': {'rate': '152/h'},
    'resource4': {'rate': '512/d'},
}

NETWORKS = ['internal', 'external']

EMAIL_SUBJECT_PREFIX = '[Anthill] '

RESOLVERS = {
    "default": {
        'internal': 'http://localhost:9502',
        'external': 'http://localhost:9502',
        'broker': 'amqp://guest:guest@localhost:5672'
    }
}

CACHES = {
    "default": {
        "BACKEND": "anthill.framework.core.cache.backends.redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/0",
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


# HTTPS = {
#     'key_file': 'key_file_path',
#     'crt_file': 'crt_file_path',
# }
HTTPS = None


##########
# CELERY #
##########

# All celery configuration options:
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#configuration
CELERY_SETTINGS = {
    'broker_url': 'amqp://guest:guest@localhost:5672',
    'broker_transport_options': {},
    'broker_connection_timeout': 4,

    'result_backend': 'redis://',
    'redis_max_connections': 150,

    'worker_concurrency': None,
    'worker_pool': 'solo',

    'task_serializer': 'json',
    'task_compression': None,
    'task_routes': {},
}

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

LOG_STREAMING = {
    'handler': {
        'class': 'anthill.framework.handlers.WatchLogFileHandler',
        'kwargs': {'handler_name': 'anthill'}
    },
    'path': '/log/',
}


##############
# RATE LIMIT #
##############

CACHES.update(
    rate_limit={
        "BACKEND": "anthill.framework.core.cache.backends.redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "anthill.framework.core.cache.backends.redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 500
            }
        }
    }
)

RATE_LIMIT_ENABLE = False
RATE_LIMIT_CACHE_PREFIX = 'rl'

# Maps resource names and its rate limit parameters.
# Rate limit has blocking and non-blocking mode.
# In blocking mode (default) rate limit prevents function execution
# either by raising RateLimitException error or executing exceeded_callback.
# In non-blocking mode rate limit do not stops function executing.
# Also we can set additional `callback` parameter, that
# runs when exceeded in non-blocking and ignored in blocking mode.
#
# Example:
#
# RATE_LIMIT_CONFIG = {
#     'user': {
#         'rate': '15/s', 'block': True, 'callback': None
#     },
#     'ip': {
#         'rate': '8/3m', 'block': True, 'callback': None
#     },
#     'create_room': {
#         'rate': '152/24h', 'block': False, 'callback': 'game.security.rate_limit.cr'
#     },
#     'send_message': {
#         'rate': '512/d', 'block': True, 'callback': None
#     }
# }
RATE_LIMIT_CONFIG = {}


##############
# WEBSOCKETS #
##############

WEBSOCKET_PING_INTERVAL = 10
WEBSOCKET_PING_TIMEOUT = 30
WEBSOCKET_MAX_MESSAGE_SIZE = None
WEBSOCKET_COMPRESSION_LEVEL = -1
WEBSOCKET_MEM_LEVEL = 6


############
# CHANNELS #
############

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "anthill.platform.core.messenger.channels.layers.backends.redis.ChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
    "internal": {
        "BACKEND": "anthill.platform.core.messenger.channels.layers.backends.redis.ChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
}


#######
# API #
#######

INTERNAL_API_CONF = 'api.v1.internal'
PUBLIC_API_URL = '/api/'


#########
# GEOIP #
#########

GEOIP_PATH = None
GEOIP_CITY = 'GeoLite2-City.mmdb'
GEOIP_COUNTRY = 'GeoLite2-Country.mmdb'


COMPRESS_RESPONSE = True


SESSION_ENGINE = 'anthill.framework.sessions.backends.cache'

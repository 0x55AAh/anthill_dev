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

# All celery configuration options:
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#configuration
CELERY = {
    'broker_url': 'amqp://guest:guest@localhost:5672',
    'result_backend': 'redis://'
}


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

HEALTH_CONTROL = False

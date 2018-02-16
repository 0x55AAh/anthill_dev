NETWORKS = ['internal', 'external']

RESOLVERS = {
    "default": {
        'internal': 'http://localhost:9502',
        'external': 'http://localhost:9502',
        'broker': 'amqp://guest:guest@localhost:5672'
    },
}

DISCOVERY_SECRET_KEY = 'DISCOVERY_SERVICE_SECRET_KEY'

CACHES = {
    "default": {
        "BACKEND": "microservices_framework.core.cache.backends.redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "microservices_framework.core.cache.backends.redis.client.DefaultClient",
        }
    }
}

# All celery configuration options:
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#configuration
CELERY = {
    'broker_url': 'amqp://guest:guest@localhost:5672',
    'result_backend': 'redis://'
}

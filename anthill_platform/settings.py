NETWORKS = ['internal', 'external']

RESOLVERS = [
    {
        'internal': 'http://localhost:9502',
        'external': 'http://localhost:9502',
        'broker': 'amqp://guest:guest@localhost:5672'
    },
]

DISCOVERY_SECRET_KEY = 'DISCOVERY_SERVICE_SECRET_KEY'

NETWORKS = ['internal', 'external', 'broker']

RESOLVERS = [
    {
        'internal': 'http://localhost:9502',
        'external': 'http://localhost:9502',
        'broker': 'amqp://guest:guest@localhost:5672'
    },
]

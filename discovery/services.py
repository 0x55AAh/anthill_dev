from anthill.platform.services import DiscoveryService
from anthill.framework.core.cache.backends.redis import get_redis_connection


class Service(DiscoveryService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = None

    async def set_storage(self):
        self.storage = get_redis_connection()

    async def setup_service(self, name, networks):
        for network_name, service_location in networks.items():
            self.storage.hset(name, network_name, service_location)

    async def remove_service(self, name):
        self.storage.delete(name)

    async def get_service_location(self, name, network_name):
        return self.storage.hget(name, network_name)

from anthill.platform.services import DiscoveryService
from anthill.framework.core.cache.backends.redis import get_redis_connection
from tornado.escape import to_basestring


class ServiceDoesNotExist(Exception):
    def __init__(self, service_name):
        self.service_name = service_name
        self.message = 'Service does not exists: %s' % service_name

    def __str__(self):
        return self.message


class Service(DiscoveryService):
    service_storage_key_prefix = 'service'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = None

    def get_service_storage_key(self, name: str) -> str:
        return ':'.join([self.service_storage_key_prefix, name])

    # noinspection PyMethodMayBeStatic
    def get_service_name_by_key(self, key: str) -> str:
        return to_basestring(key).split(':', maxsplit=1)[1]

    async def setup_storage(self) -> None:
        self.storage = get_redis_connection()

    async def setup_service(self, name: str, networks: dict) -> None:
        for network_name, service_location in networks.items():
            key = self.get_service_storage_key(name)
            self.storage.hset(key, network_name, service_location)

    async def remove_service(self, name: str) -> None:
        key = self.get_service_storage_key(name)
        self.storage.delete(key)

    async def is_service_exists(self, name: str) -> bool:
        key = self.get_service_storage_key(name)
        return self.storage.exists(key)

    async def get_service(self, name: str, networks: list=None) -> dict:
        if not await self.is_service_exists(name):
            raise ServiceDoesNotExist(name)
        key = self.get_service_storage_key(name)
        if networks is None:
            networks = self.storage.hkeys(key)
        return {
            to_basestring(network): to_basestring(self.storage.hget(key, network))
            for network in networks
        }

    async def list_services(self) -> list:
        pattern = ':'.join([self.service_storage_key_prefix, '*'])
        return list(map(self.get_service_name_by_key, self.storage.keys(pattern)))

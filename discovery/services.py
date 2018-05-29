from anthill.platform.services import DiscoveryService
from anthill.framework.core.cache.backends.redis import get_redis_connection
from tornado.escape import to_basestring
import json
import uuid


class ServiceDoesNotExist(Exception):
    def __init__(self, service_name):
        self.service_name = service_name
        self.message = 'Service does not exists: %s' % service_name

    def __str__(self):
        return self.message


class Service(DiscoveryService):
    registered_service_storage_key_prefix = 'service'
    requested_for_register_service_storage_key_prefix = 'request_for_register'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = None

    def get_service_storage_key(self, name: str) -> str:
        return ':'.join([self.registered_service_storage_key_prefix, name])

    def get_entity_by_key(self, key: str) -> str:
        key = to_basestring(key)
        return key.split(':', maxsplit=1)[1]

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
        pattern = ':'.join([self.registered_service_storage_key_prefix, '*'])
        return list(map(self.get_entity_by_key, self.storage.keys(pattern)))

    # Request for register service

    def create_request_storage_key(self) -> tuple:
        request_id = str(uuid.uuid4())
        return request_id, self.get_request_storage_key_by_id(request_id)

    def get_request_storage_key_by_id(self, request_id: str) -> str:
        return ':'.join([
            self.requested_for_register_service_storage_key_prefix,
            request_id
        ])

    async def create_request_for_register_service(self, name: str, networks: dict) -> str:
        request_id, key = self.create_request_storage_key()
        self.storage.hset(key, name, json.dumps(networks))
        return request_id

    async def delete_request_for_register_service(self, request_id: str) -> None:
        key = self.get_request_storage_key_by_id(request_id)
        self.storage.delete(key)

    async def get_request_for_register_service(self, request_id: str) -> tuple:
        key = self.get_request_storage_key_by_id(request_id)
        service_name = self.storage.hkeys(key)[0]
        networks = self.storage.hget(key, service_name)
        return service_name, json.loads(networks)

    async def get_requests_for_register_service(self) -> dict:
        def _networks(key_):
            service_name_ = self.storage.hkeys(key_)[0]
            networks_ = self.storage.hget(key_, service_name_)
            return dict([service_name_, json.loads(networks_)])

        def _request_id(key_):
            return self.get_entity_by_key(key_)

        pattern = ':'.join([self.requested_for_register_service_storage_key_prefix, '*'])
        return {_request_id(key): _networks(key) for key in self.storage.keys(pattern)}

    # /Request for register service

from anthill.platform.services import DiscoveryService
from anthill.framework.core.cache.backends.redis import get_redis_connection
import json
import uuid


class Service(DiscoveryService):
    registered_service_storage_key_prefix = 'service'
    requested_for_register_service_storage_key_prefix = 'request_for_register'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = None

    def get_service_storage_key(self, name: str) -> str:
        return ':'.join([self.registered_service_storage_key_prefix, name])

    def get_entity_by_key(self, key: str) -> str:
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

    async def get_service(self, name: str, networks: list=None) -> tuple:
        if networks is None:
            networks = self.storage.hkeys(name)
        key = self.get_service_storage_key(name)
        return name, {
                network: self.storage.hget(key, network)
                for network in networks
            }

    async def get_registered_services(self) -> list:
        keys = self.storage.keys(self.registered_service_storage_key_prefix)
        return [self.get_entity_by_key(key) for key in keys]

    # Request for register service

    def create_request_storage_key(self) -> tuple:
        request_id = str(uuid.uuid4())
        return request_id, self.get_request_storage_key_by_id(request_id)

    def get_request_storage_key_by_id(self, request_id: str) -> str:
        return ':'.join([self.requested_for_register_service_storage_key_prefix, request_id])

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
        result = {}
        for key in self.storage.keys(self.requested_for_register_service_storage_key_prefix):
            request_id = self.get_entity_by_key(key)
            service_name = self.storage.hkeys(key)[0]
            networks = self.storage.hget(key, service_name)
            result[request_id] = {service_name: json.loads(networks)}
        return result

    # /Request for register service

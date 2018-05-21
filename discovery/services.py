from anthill.platform.services import DiscoveryService
from anthill.framework.core.cache.backends.redis import get_redis_connection


class Service(DiscoveryService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = None

    async def setup_storage(self) -> None:
        self.storage = get_redis_connection()

    async def setup_service(self, name: str, networks: dict) -> None:
        for network_name, service_location in networks.items():
            self.storage.hset(name, network_name, service_location)

    async def remove_service(self, name: str) -> None:
        self.storage.delete(name)

    async def get_service(self, name: str, networks: list) -> tuple:
        return name, {
                network: self.storage.hget(name, network)
                for network in networks
            }

    async def get_registered_services(self) -> list:
        return self.storage.keys()

    # Request for register service

    async def create_request_for_register_service(self, name: str, networks: dict) -> str:
        pass

    async def delete_request_for_register_service(self, request_id: str) -> None:
        pass

    async def get_request_for_register_service(self, request_id: str) -> tuple:
        pass

    async def get_requests_for_register_service(self) -> dict:
        pass

    # /Request for register service

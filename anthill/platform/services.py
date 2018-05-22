from anthill.framework.core.servers import BaseService as _BaseService
from anthill.platform.utils.celery import CeleryMixin
from anthill.platform.api.internal import Internal
from anthill.framework.apps import app
import logging

logger = logging.getLogger('anthill.server')


class ServiceAlreadyRegistered(Exception):
    def __init__(self, name, message=None):
        super().__init__(message)
        self.name = name


class BaseService(CeleryMixin, _BaseService):
    def __init__(self, handlers=None, default_host=None, transforms=None, **kwargs):
        super().__init__(handlers, default_host, transforms, **kwargs)
        self.internal = Internal()

    def setup(self) -> None:
        log_streaming_config = getattr(self.config, 'LOG_STREAMING', None)
        if log_streaming_config:
            from tornado.web import url
            from anthill.framework.handlers import LogStreamingHandler
            custom_handler_class = log_streaming_config.get('handler', {}).get('class')
            if not custom_handler_class:
                handler_class = LogStreamingHandler
            else:
                from anthill.framework.utils.module_loading import import_string
                handler_class = import_string(custom_handler_class)
            handler_kwargs = log_streaming_config.get('handler', {}).get('kwargs', dict(handler_name='anthill'))
            url_name = log_streaming_config.get('name', 'log')
            url_path = log_streaming_config.get('path', '/log/').rstrip('/') + '/'
            self.add_handlers(r'^(.*)$', [
                url(r'^%s?$' % url_path, handler_class, kwargs=handler_kwargs, name=url_name),
            ])
        super().setup()

    def get_server_kwargs(self) -> dict:
        kwargs = super().get_server_kwargs()
        kwargs.update(xheaders=True)
        return kwargs

    async def on_start(self) -> None:
        logger.info('Service `%s` started.' % self.name)
        self.start_celery()

    async def on_stop(self) -> None:
        logger.info('Service `%s` stopped.' % self.name)


class PlainService(BaseService):
    async def register_on_discovery(self):
        service_name = app.label
        networks_data = app.registry_entry

    async def unregister_on_discovery(self):
        pass

    async def discover(self, names=None, network=None):
        pass

    async def on_start(self) -> None:
        await self.register_on_discovery()
        await super().on_start()


class AdminService(PlainService):
    pass


class DiscoveryService(BaseService):
    cleanup_storage_on_stop = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registry = app.registered_services

    async def on_start(self) -> None:
        await super().on_start()
        await self.setup_storage()
        await self.setup_services()

    async def on_stop(self) -> None:
        await super().on_stop()
        if self.cleanup_storage_on_stop:
            await self.remove_services()

    async def setup_services(self) -> None:
        for service_name, networks in self.registry.items():
            await self.setup_service(service_name, networks)

    async def remove_services(self) -> None:
        for service_name in await self.get_registered_services():
            await self.remove_service(service_name)

    async def get_registered_services(self) -> list:
        raise NotImplementedError

    async def setup_service(self, name: str, networks: dict) -> None:
        raise NotImplementedError

    async def remove_service(self, name: str) -> None:
        raise NotImplementedError

    async def get_service(self, name: str, networks: list=None) -> tuple:
        raise NotImplementedError

    async def setup_storage(self) -> None:
        raise NotImplementedError

    # Request for register service

    async def create_request_for_register_service(self, name: str, networks: dict) -> str:
        raise NotImplementedError

    async def delete_request_for_register_service(self, request_id: str) -> None:
        raise NotImplementedError

    async def get_request_for_register_service(self, request_id: str) -> tuple:
        raise NotImplementedError

    async def get_requests_for_register_service(self) -> dict:
        raise NotImplementedError

    async def register_service(self, request_id: str) -> None:
        name, networks = await self.get_request_for_register_service(request_id)
        if name in await self.get_registered_services():
            raise ServiceAlreadyRegistered(name)
        await self.setup_service(name, networks)

    async def unregister_service(self, name: str) -> None:
        await self.remove_service(name)

    # /Request for register service

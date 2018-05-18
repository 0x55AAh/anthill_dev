from anthill.framework.core.servers import BaseService as _BaseService
from anthill.framework.apps import app
from anthill.platform.utils.celery import CeleryMixin
from anthill.framework.core.cache import cache
import logging
import json

logger = logging.getLogger('anthill.server')


class RegisterNotAllowed(Exception):
    pass


class BaseService(CeleryMixin, _BaseService):
    def setup(self):
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

    def get_server_kwargs(self):
        kwargs = super().get_server_kwargs()
        kwargs.update(xheaders=True)
        return kwargs

    async def on_start(self):
        logger.info('Service `%s` started.' % self.name)
        self.start_celery()

    async def on_stop(self):
        logger.info('Service `%s` stopped.' % self.name)


class PlainService(BaseService):
    async def register_on_discovery(self):
        label = app.label
        data = app.registry_entry
        key = 'DISCOVERY_SERVICE_SECRET_KEY'

    async def unregister_on_discovery(self):
        pass

    async def discover(self, names=None, network=None):
        pass

    async def on_start(self):
        await self.register_on_discovery()
        await super().on_start()


class AdminService(PlainService):
    pass


class DiscoveryService(BaseService):
    cleanup_storage_on_stop = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registry = app.registered_services

    async def on_start(self):
        await super().on_start()
        await self.set_storage()
        await self.setup_services()

    async def on_stop(self):
        await super().on_stop()
        if self.cleanup_storage_on_stop:
            await self.remove_services()

    async def set_storage(self):
        raise NotImplementedError

    async def register_service(self, name, data, key):
        if not self.register_allowed(key):
            raise RegisterNotAllowed
        entry = {
            name: data
        }
        # Add the entry to discovery services registry

    async def unregister_service(self, name):
        pass

    async def setup_services(self):
        for service_name, networks in self.registry.items():
            await self.setup_service(service_name, networks)

    async def remove_services(self):
        for service_name in await self.get_installed_services():
            await self.remove_service(service_name)

    async def get_installed_services(self):
        raise NotImplementedError

    async def setup_service(self, name, networks):
        raise NotImplementedError

    async def remove_service(self, name):
        raise NotImplementedError

    async def get_service_location(self, name, network):
        raise NotImplementedError

    def register_allowed(self, key):
        if app.settings.SECRET_KEY == key:
            return True
        return False

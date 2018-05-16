from anthill.framework.core.servers import BaseService as _BaseService
from anthill.framework.apps import app
from anthill.platform.utils.celery import CeleryMixin
import logging

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

    async def discover(self, names=None, network=None):
        pass

    async def on_start(self):
        await self.register_on_discovery()
        await super().on_start()


class AdminService(PlainService):
    pass


class DiscoveryService(BaseService):
    async def register_service(self, name, data, key):
        if not self.register_allowed(key):
            raise RegisterNotAllowed
        entry = {
            name: data
        }
        # Add the entry to discovery services registry

    def register_allowed(self, key):
        if app.settings.SECRET_KEY == key:
            return True
        return False

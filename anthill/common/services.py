import logging
from anthill.framework.core.celery.worker import start_worker
from anthill.framework.core.servers import BaseService as _BaseService
from anthill.framework.apps import app
from .utils.celery import celery

logger = logging.getLogger('anthill.server')


class BaseService(_BaseService):
    def get_server_kwargs(self):
        return dict(xheaders=True)

    async def __on_internal_receive__(self, context, method, *args, **kwargs):
        pass

    async def on_start(self):
        logger.info('Service \'%s\' started.' % self.name)
        if getattr(app.settings, 'USE_CELERY', False):
            with start_worker(app=celery):
                pass

    async def on_stop(self):
        logger.info('Service \'%s\' stopped.' % self.name)


class PlainService(BaseService):
    async def register_on_discovery(self):
        label = app.label
        data = app.registry_entry
        key = 'DISCOVERY_SERVICE_SECRET_KEY'

    async def discover(self, names=None, network=None):
        pass

    async def on_start(self):
        await self.register_on_discovery()
        await super(PlainService, self).on_start()


class AdminService(PlainService):
    pass


class RegisterNotAllowed(Exception):
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

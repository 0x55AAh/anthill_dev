import logging
from tornado.gen import coroutine
from microservices_framework.core.service import BaseService as _BaseService

logger = logging.getLogger('app.server')


class BaseService(_BaseService):
    def get_server_kwargs(self):
        return {
            'xheaders': True
        }

    @coroutine
    def __on_internal_receive__(self, context, method, *args, **kwargs):
        pass

    @coroutine
    def on_start(self):
        logger.info('Service \'%s\' started.' % self.name)

    @coroutine
    def on_stop(self):
        logger.info('Service \'%s\' stopped.' % self.name)


class RequestForDiscoveryServiceSingleMixin:
    def discover_service(self, name, network=None):
        pass


class RequestForDiscoveryServiceMultipleMixin:
    def discover_services(self, names=None):
        pass


class ServiceWithDiscoverySingle(BaseService, RequestForDiscoveryServiceSingleMixin):
    pass


class ServiceWithDiscoveryMultiple(BaseService, RequestForDiscoveryServiceSingleMixin):
    pass

from tornado.ioloop import PeriodicCallback
from anthill.framework.utils.decorators import method_decorator, retry
from anthill.framework.core.servers import BaseService as _BaseService
from anthill.platform.utils.celery import CeleryMixin
from anthill.platform.api.internal import JSONRPCInternalConnection, RequestTimeoutError
from anthill.framework.utils.geoip import GeoIP2
from functools import partial
from tornado.web import url
import logging

logger = logging.getLogger('anthill.application')


class ServiceAlreadyRegistered(Exception):
    def __init__(self, name, message=None):
        super().__init__(message)
        self.name = name


class BaseService(CeleryMixin, _BaseService):
    internal_api_connection_class = JSONRPCInternalConnection

    def __init__(self, handlers=None, default_host=None, transforms=None, **kwargs):
        super().__init__(handlers, default_host, transforms, **kwargs)
        self.internal_connection = self.internal_api_connection_class(service=self)
        if getattr(self.config, 'GEOIP_PATH', None):
            self.gis = GeoIP2()
            logger.debug('Geo position tracking system status: ENABLED.')
        else:
            self.gis = None
            logger.debug('Geo position tracking system status: DISABLED.')

    def setup(self) -> None:
        def url_pattern(_url, float_slash=True):
            _url, end = _url.rstrip('/'), ''
            if float_slash is not None:
                end += '/?' if float_slash else '/'
            return r'^{url}{end}$'.format(url=_url, end=end)

        # Log streaming
        log_streaming_config = getattr(self.config, 'LOG_STREAMING', None)
        if log_streaming_config:
            from anthill.framework.handlers import WatchLogFileHandler
            custom_handler_class = log_streaming_config.get('handler', {}).get('class')
            if not custom_handler_class:
                handler_class = WatchLogFileHandler
            else:
                from anthill.framework.utils.module_loading import import_string
                handler_class = import_string(custom_handler_class)
            handler_kwargs = log_streaming_config.get('handler', {}).get('kwargs', dict(handler_name='anthill'))
            log_streaming_url = log_streaming_config.get('path', '/log/')
            self.add_handlers(self.app.host_regex, [
                url(url_pattern(log_streaming_url), handler_class, kwargs=handler_kwargs, name='log'),
            ])
            logger.debug('Log streaming installed on %s.' % log_streaming_url)

        # Public API
        from anthill.framework.handlers import GraphQLHandler
        public_api_url = getattr(self.config, 'PUBLIC_API_URL', '/api/')
        self.add_handlers(self.app.host_regex, [
            url(url_pattern(public_api_url), GraphQLHandler, dict(graphiql=True), name='api')])
        logger.debug('Public api installed on %s.' % public_api_url)

        super().setup()

    def get_server_kwargs(self) -> dict:
        kwargs = super().get_server_kwargs()
        return kwargs

    async def on_start(self) -> None:
        await self.internal_connection.connect()
        self.start_celery()
        logger.info('Service `%s` started.' % self.name)

    async def on_stop(self) -> None:
        await self.internal_connection.disconnect()
        logger.info('Service `%s` stopped.' % self.name)


class PlainService(BaseService):
    auto_register_on_discovery = True
    register_max_retries = 0

    def __init__(self, handlers=None, default_host=None, transforms=None, **kwargs):
        super().__init__(handlers, default_host, transforms, **kwargs)
        self.discovery_request = partial(self.internal_connection.request, 'discovery')

    @method_decorator(retry(max_retries=register_max_retries, delay=0,
                            on_exception=lambda func, e:
                                logger.fatal('Service `discovery` is unreachable.'),
                            exception_types=(RequestTimeoutError,)))
    async def register_on_discovery(self) -> None:
        kwargs = {
            'name': self.name,
            'networks': self.app.registry_entry
        }
        await self.discovery_request('set_service_bulk', **kwargs)
        logger.info('Connected to `discovery` service.')

    async def unregister_on_discovery(self) -> None:
        await self.discovery_request('remove_service', name=self.name)
        logger.info('Disconnected from `discovery` service.')

    async def discover(self, name: str, network: str=None) -> dict:
        return await self.discovery_request('get_service', name=name, network=network)

    async def on_start(self) -> None:
        await super().on_start()
        if self.auto_register_on_discovery:
            await self.register_on_discovery()

    async def on_stop(self) -> None:
        if self.auto_register_on_discovery:
            await self.unregister_on_discovery()
        await super().on_stop()


class AdminService(PlainService):
    pass


class DiscoveryService(BaseService):
    cleanup_storage_on_stop = True
    cleanup_services_period = 1
    ping_services = True
    ping_max_retries = 1
    ping_timeout = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ping_monitor = None
        if self.ping_services:
            self.ping_monitor = PeriodicCallback(
                self.check_services, self.cleanup_services_period * 1000)
        self.registry = self.app.registry

    async def on_start(self) -> None:
        await super().on_start()
        await self.setup_storage()
        await self.setup_services()
        if self.ping_monitor is not None:
            self.ping_monitor.start()

    async def on_stop(self) -> None:
        await super().on_stop()
        if self.cleanup_storage_on_stop:
            await self.remove_services()
        if self.ping_monitor is not None:
            self.ping_monitor.stop()

    @method_decorator(retry(max_retries=ping_max_retries, delay=0,
                            exception_types=(RequestTimeoutError, KeyError, TypeError)))
    async def is_service_alive(self, name):
        internal_request = partial(self.internal_connection.request, name)
        try:
            response = await internal_request('ping', timeout=self.ping_timeout)
            return response['message'] == 'pong'
        except Exception as e:
            logger.error('Service `%s` is unreachable. %s' % (name, str(e)))
            raise

    async def check_services(self):
        for name in self.registry.keys():
            if name == self.name:
                # Prevent self pinging
                continue
            if not await self.is_service_alive(name):
                await self.remove_service(name)
            else:
                if name not in await self.list_services():
                    await self.setup_service(name, self.registry[name])

    async def setup_services(self) -> None:
        for name, networks in self.registry.items():
            await self.setup_service(name, networks)

    async def remove_services(self) -> None:
        for name in await self.list_services():
            await self.remove_service(name)

    async def list_services(self) -> list:
        """Returns a list of services names."""
        raise NotImplementedError

    async def setup_service(self, name: str, networks: dict) -> None:
        raise NotImplementedError

    async def remove_service(self, name: str) -> None:
        raise NotImplementedError

    async def is_service_exists(self, name: str) -> bool:
        raise NotImplementedError

    async def get_service(self, name: str, networks: list=None) -> dict:
        raise NotImplementedError

    async def setup_storage(self) -> None:
        raise NotImplementedError

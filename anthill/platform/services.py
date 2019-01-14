from tornado.ioloop import PeriodicCallback
from anthill.framework.utils.decorators import method_decorator, retry
from anthill.framework.utils import timezone
from anthill.framework.core.servers import BaseService as _BaseService
from anthill.framework.core.cache import caches
from anthill.framework.handlers.socketio import socketio_client
from anthill.platform.utils.celery import CeleryMixin
from anthill.platform.api.internal import (
    JSONRPCInternalConnection, RequestTimeoutError, RequestError)
from anthill.framework.utils.geoip import GeoIP2
from tornado.httpclient import HTTPClientError
from functools import partial
from tornado.web import url
import socketio
import logging

logger = logging.getLogger('anthill.application')


class MasterRole:
    """Mixin class for enabling `master` role on service."""


class ControllerRole:
    """Mixin class for enabling `controller` role on service."""


def dict_filter(d, keys=None):
    if keys:
        return dict((k, d[k]) for k in d if k in keys)
        # return dict(filter(lambda x: x[0] in keys, d.items()))
    else:
        return d


class ServiceDoesNotExist(Exception):
    def __init__(self, service_name):
        self.service_name = service_name
        self.message = 'Service does not exists: %s' % service_name

    def __str__(self):
        return self.message


class ServiceAlreadyRegistered(Exception):
    def __init__(self, name, message=None):
        super().__init__(message)
        self.name = name


def _url_pattern(url_, float_slash=True):
    end = ''
    if float_slash is not None:
        end = '/?' if float_slash else '/'
        url_ = url_.rstrip('/')
    return r'^{url}{end}$'.format(url=url_, end=end)


class UpdateManager:
    schemes = ('git', 'pip', 'pip+git')

    def __init__(self, scheme='git'):
        self.scheme = scheme

    async def versions(self):
        pass

    async def current_version(self):
        pass

    async def update(self, version=None):
        pass


class MessengerClient:
    def __init__(self, url, namespace='/messenger'):
        self.url = url
        self.socketio_client = socketio_client
        self.namespace = namespace or '/'
        self.socketio_client.register_namespace(self.Namespace(self.namespace))

    class Namespace(socketio.AsyncClientNamespace):
        def on_connect(self):
            logger.debug('Connected to messenger.')

        def on_disconnect(self):
            logger.debug('Disconnected from messenger.')

    def __repr__(self):
        return "<MessengerClient(url=%r, namespace=%r)>" % (self.url, self.namespace)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.close()

    async def connect(self):
        await self.socketio_client.connect(self.url, namespaces=[self.namespace])

    async def send(self, event, data=None, namespace=None, callback=None):
        await self.socketio_client.emit(
            event, data=data, namespace=namespace or self.namespace, callback=callback)
        logger.debug('Message has been sent.')

    def close(self):
        self.socketio_client.disconnect()


class BaseService(CeleryMixin, _BaseService):
    internal_api_connection_class = JSONRPCInternalConnection

    def __init__(self, handlers=None, default_host=None, transforms=None, **kwargs):
        super().__init__(handlers, default_host, transforms, **kwargs)
        self.gis = None
        if getattr(self.config, 'GEOIP_PATH', None):
            self.gis = GeoIP2()
        logger.debug('Geo position tracking system status: '
                     '%s.' % 'ENABLED' if self.gis else 'DISABLED')
        self.started_at = None
        self.update_manager = UpdateManager()

    @property
    def internal_connection(self):
        return self.internal_api_connection_class(service=self)

    @property
    def internal_request(self):
        return self.internal_connection.request

    @property
    def uptime(self):
        if self.started_at is not None:
            return timezone.now() - self.started_at

    def setup_public_api(self):
        public_api_url = getattr(self.config, 'PUBLIC_API_URL', None)
        if public_api_url is not None:
            from anthill.framework.handlers import GraphQLHandler
            self.add_handlers(self.app.host_regex, [
                url(_url_pattern(public_api_url), GraphQLHandler, dict(graphiql=True), name='api')])
            logger.debug('Public api installed on %s.' % public_api_url)
        else:
            logger.debug('Public api not installed.')

    def setup_log_streaming(self):
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
                url(_url_pattern(log_streaming_url), handler_class, kwargs=handler_kwargs, name='log'),
            ])
            logger.debug('Log streaming installed on %s.' % log_streaming_url)
        else:
            logger.debug('Log streaming not installed.')

    def setup(self) -> None:
        self.setup_log_streaming()
        self.setup_public_api()
        super().setup()

    async def on_start(self) -> None:
        await self.internal_connection.connect()
        self.start_celery()
        self.started_at = timezone.now()  # TODO: already started?
        logger.info('Service `%s` started.' % self.name)

    async def on_stop(self) -> None:
        await self.internal_connection.disconnect()
        logger.info('Service `%s` stopped.' % self.name)


class PlainService(BaseService):
    auto_register_on_discovery = True
    discovery_name = 'discovery'
    message_name = 'message'
    admin_name = 'admin'

    def __init__(self, handlers=None, default_host=None, transforms=None, **kwargs):
        super().__init__(handlers, default_host, transforms, **kwargs)
        self.messenger_client = None

    def setup(self) -> None:
        self.settings.update(messenger_url=None)
        self.settings.update(registered_services={})
        self.setup_internal_request_methods()
        super().setup()

    # noinspection PyAttributeOutsideInit
    def setup_internal_request_methods(self):
        self.discovery_request = partial(self.internal_request, self.discovery_name)
        self.message_request = partial(self.internal_request, self.message_name)
        self.admin_request = partial(self.internal_request, self.admin_name)

    @method_decorator(retry(max_retries=0, delay=3, exception_types=(RequestError,),
                            on_exception=lambda func, e: logger.error('Service `discovery` is unreachable.'),))
    async def register_on_discovery(self) -> None:
        kwargs = dict(name=self.name, networks=self.app.registry_entry)
        await self.discovery_request('set_service_bulk', **kwargs)
        logger.info('Connected to `discovery` service.')

    async def unregister_on_discovery(self) -> None:
        await self.discovery_request('remove_service', name=self.name)
        logger.info('Disconnected from `discovery` service.')

    async def discover(self, name: str, network: str = None) -> dict:
        return await self.discovery_request('get_service', name=name, network=network)

    @method_decorator(retry(max_retries=0, delay=3, exception_types=(RequestError,),
                            on_exception=lambda func, e: logger.error('Cannot get registered services. Retry...'), ))
    async def set_registered_services(self) -> None:
        registered_services = await self.discovery_request('get_registered_services')
        self.settings.update(registered_services=registered_services)

    @method_decorator(retry(max_retries=0, delay=3, exception_types=(RequestError,),
                            on_exception=lambda func, e: logger.error('Cannot get login url. Retry...'), ))
    async def set_login_url(self) -> None:
        login_url = await self.admin_request('get_login_url')
        self.settings.update(login_url=login_url)
        logger.debug('Login url: %s' % login_url)

    def create_messenger_client(self) -> MessengerClient:
        messenger_url = self.settings['registered_services'][self.message_name]['internal']
        return MessengerClient(url=messenger_url)

    async def messenger_client_connect(self) -> None:
        self.messenger_client = self.create_messenger_client()
        await self.messenger_client.connect()

    async def on_start(self) -> None:
        await super().on_start()
        if self.auto_register_on_discovery:
            await self.register_on_discovery()
        await self.set_registered_services()
        await self.set_login_url()
        await self.messenger_client_connect()

    async def on_stop(self) -> None:
        self.messenger_client.close()
        if self.auto_register_on_discovery:
            await self.unregister_on_discovery()
        await super().on_stop()


class AdminService(PlainService):
    update_services_meta_period = 5
    update_services_meta = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.update_services_meta:
            self.services_meta_updater = PeriodicCallback(
                self.set_services_meta, self.update_services_meta_period * 1000)
        else:
            self.services_meta_updater = None

    def setup(self) -> None:
        self.settings.update(services_meta={})
        super().setup()

    async def get_services_metadata(self, exclude_names=None):
        services_metadata = []
        exclude_names = exclude_names or []
        try:
            services_names = await self.discovery_request('get_services_names')
        except RequestTimeoutError:
            pass  # ¯\_(ツ)_/¯
        else:
            for name in services_names:
                if name in exclude_names:
                    continue
                try:
                    metadata = await self.internal_request(name, method='get_service_metadata')
                    services_metadata.append(metadata)
                except RequestTimeoutError:
                    pass  # ¯\_(ツ)_/¯
        return services_metadata

    @method_decorator(retry(max_retries=0, delay=3, exception_types=(RequestError,),
                            on_exception=lambda func, e: logger.error('Cannot get services meta. Retry...'), ))
    async def set_services_meta(self):
        services_meta = await self.get_services_metadata(exclude_names=[self.name])
        self.settings.update(services_meta=services_meta)

    async def on_start(self) -> None:
        await super().on_start()
        await self.set_services_meta()
        if self.services_meta_updater is not None:
            self.services_meta_updater.start()

    async def on_stop(self) -> None:
        if self.services_meta_updater is not None:
            self.services_meta_updater.stop()
        await super().on_stop()


class APIGatewayService(AdminService):
    pass


class DiscoveryService(BaseService):
    cleanup_storage_on_start = True
    cleanup_services_period = 5
    ping_services = True
    ping_max_retries = 1
    ping_timeout = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.ping_services:
            self.ping_monitor = PeriodicCallback(
                self.check_services, self.cleanup_services_period * 1000)
        else:
            self.ping_monitor = None
        self.registry = self.app.registry
        self.storage = caches['services']

    async def on_start(self) -> None:
        await super().on_start()
        await self.setup_services(cleanup=self.cleanup_storage_on_start)
        if self.ping_monitor is not None:
            self.ping_monitor.start()

    async def on_stop(self) -> None:
        await super().on_stop()
        if self.ping_monitor is not None:
            self.ping_monitor.stop()

    @method_decorator(retry(max_retries=ping_max_retries, delay=0,
                            exception_types=(RequestTimeoutError, KeyError, TypeError)))
    async def is_service_alive(self, name):
        internal_request = partial(self.internal_request, name)
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

    async def setup_services(self, cleanup=False) -> None:
        if cleanup:
            await self.remove_services()
        self.storage.set_many(self.registry, timeout=None)

    async def remove_services(self) -> None:
        self.storage.delete_many(keys=self.registry.keys())

    async def list_services(self) -> list:
        """Returns a list of services names."""
        return list(self.storage.get_many(keys=self.registry.keys()).keys())

    async def setup_service(self, name: str, networks: dict) -> None:
        self.storage.set(name, networks, timeout=None)

    async def remove_service(self, name: str) -> None:
        self.storage.delete(name)

    async def is_service_exists(self, name: str) -> bool:
        return name in self.storage

    async def get_service(self, name: str, networks: list = None) -> dict:
        if not await self.is_service_exists(name):
            raise ServiceDoesNotExist(name)
        return dict_filter(self.storage.get(name), keys=networks)

    async def get_services(self) -> dict:
        return self.storage.get_many(keys=self.registry.keys())

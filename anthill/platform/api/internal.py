from tornado.gen import with_timeout
from tornado.util import TimeoutError

from anthill.framework.utils.singleton import Singleton
from anthill.platform.core.messenger.channels.layers import get_channel_layer
from anthill.platform.core.messenger.channels.exceptions import InvalidChannelLayerError
from tornado.ioloop import IOLoop
from tornado.concurrent import Future
import functools
import datetime

from anthill.framework.core.jsonrpc.exceptions import JSONRPCInvalidRequestException
from anthill.framework.core.jsonrpc.jsonrpc import JSONRPCRequest
from anthill.framework.core.jsonrpc.manager import JSONRPCResponseManager
from anthill.framework.core.jsonrpc.dispatcher import Dispatcher
from anthill.framework.core.jsonrpc.utils import DatetimeDecimalEncoder
import json


__all__ = [
    'InternalConnection', 'JSONRPCInternalConnection', 'InternalAPIError',
    'as_internal', 'api', 'InternalAPI'
]


class InternalAPIError(Exception):
    pass


class InternalAPIRequestTimeoutError(Exception):
    pass


class InternalAPI(Singleton):
    methods = []

    def __init__(self):
        self.service = None

    def __iter__(self):
        return iter(self.methods)

    def __getitem__(self, key):
        return self.methods[key]

    def __repr__(self):
        return repr(self.methods)

    def __len__(self):
        return len(self.methods)

    def as_internal(self):
        """Decorator marks function as an internal api method."""

        def decorator(func):
            self.methods.append(func.__name__)
            setattr(self.__class__, func.__name__, func)
            return func

        return decorator


api = InternalAPI()
as_internal = api.as_internal


class InternalConnection(Singleton):
    """
    Implements communications between services.
    """
    message_type = channel_alias = 'internal'
    channel_group_name_prefix = 'internal'
    request_timeout = 10

    def __init__(self, service=None):
        self.channel_layer = None
        self.channel_name = None
        self.channel_receive = None
        self.service = service
        self._responses = {}
        self._current_request_id = 0
        super().__init__()

    def channel_group_name(self, service=None) -> str:
        service_name = service or self.service.name
        return '_'.join([self.channel_group_name_prefix, service_name])

    async def channel_receive_callback(self) -> None:
        if self.channel_receive:
            while True:
                message = await self.channel_receive()
                await self.on_message(message)

    async def on_message(self, message: dict) -> None:
        raise NotImplementedError

    async def connect(self) -> None:
        IOLoop.current().add_callback(self.channel_receive_callback)
        self.channel_layer = get_channel_layer(alias=self.channel_alias)
        if self.channel_layer is not None:
            self.channel_name = await self.channel_layer.new_channel(prefix=self.service.app.label)
            self.channel_receive = functools.partial(self.channel_layer.receive, self.channel_name)
            await self.channel_layer.group_add(self.channel_group_name(), self.channel_name)

    async def disconnect(self) -> None:
        await self.channel_layer.group_discard(
            self.channel_group_name(), self.channel_name)

    async def send(self, service: str, message: dict) -> None:
        try:
            await self.channel_layer.group_send(self.channel_group_name(service), message)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is not configured or doesn't support groups")

    def next_request_id(self):
        self._current_request_id += 1
        return self._current_request_id

    async def request(self, service: str, method: str, timeout: int=None, **kwargs) -> dict:
        request_id = self.next_request_id()
        message = {
            'type': self.message_type,
            'service': self.service.name,
            'payload': {
                'jsonrpc': '2.0',
                'method': method,
                'params': kwargs,
                'id': request_id
            }
        }
        self._responses[request_id] = future = Future()
        await self.send(service, message)
        timeout = timeout or self.request_timeout
        try:
            return await with_timeout(datetime.timedelta(seconds=timeout), future)
        except TimeoutError:
            raise InternalAPIRequestTimeoutError(
                'Service `%s` not responded for %s sec' % (service, timeout))
        finally:
            del self._responses[request_id]


class JSONRPCInternalConnection(InternalConnection):
    message_type = 'internal_json_rpc'

    def __init__(self, service=None, dispatcher=None):
        super().__init__(service)
        self.dispatcher = dispatcher if dispatcher is not None else Dispatcher()
        for method_name in api:
            self.dispatcher.add_method(getattr(api, method_name))

    async def on_message(self, message: dict) -> None:
        service = message['service']
        payload = message['payload']

        if isinstance(payload, str):
            payload = json.loads(payload)

        def has_keys(d, keys):
            for k in d.keys():
                if k in keys:
                    return True
            return False

        def get_result(d, keys):
            for k, v in d.items():
                if k in keys:
                    return v

        if has_keys(payload, ('result', 'error')):
            result = get_result(payload, ('result', 'error'))
            request_id = payload.get('id')
            future = self._responses[request_id]
            future.set_result(result)
        elif 'method' in payload:
            payload = json.dumps(payload)
            try:
                json_rpc_request = JSONRPCRequest.from_json(payload)
            except (TypeError, ValueError, JSONRPCInvalidRequestException):
                response = await JSONRPCResponseManager.handle(payload, self.dispatcher)
            else:
                json_rpc_request.params = json_rpc_request.params or {}
                response = await JSONRPCResponseManager.handle_request(
                    json_rpc_request, self.dispatcher)

            def response_serialize(obj):
                """Serializes response's data object to JSON."""
                return json.dumps(obj, cls=DatetimeDecimalEncoder)

            if response:
                response.serialize = response_serialize
                response = response.json

            message = dict(payload=response, service=self.service.name, type=self.message_type)

            await self.send(service, message)

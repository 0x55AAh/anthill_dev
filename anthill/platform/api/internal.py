from anthill.framework.utils.singleton import Singleton
from anthill.platform.core.messenger.channels.layers import get_channel_layer
from anthill.platform.core.messenger.channels.exceptions import InvalidChannelLayerError
from tornado.ioloop import IOLoop
from tornado.concurrent import Future
import functools

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


class InternalAPI(Singleton):
    methods = dict()

    def __iter__(self):
        return iter(self.methods.values())

    def as_internal(self):
        """Decorator marks function as an internal api method."""

        def decorator(func):
            self.methods[func.__name__] = func
            return func

        return decorator


api = InternalAPI()
as_internal = api.as_internal


class InternalConnection(Singleton):
    """
    Implements communications between services.
    """
    message_type = 'internal'

    def __init__(self, service):
        self.channel_layer = None
        self.channel_name = None
        self.channel_receive = None
        self.channel_group_name_prefix = 'internal'
        self.service = service
        self._responses = {}
        self._current_request_id = 0
        super().__init__()

    def channel_group_name(self, service=None) -> str:
        service = service or self.service
        return '_'.join([self.channel_group_name_prefix, service.app.label])

    async def channel_receive_callback(self) -> None:
        if self.channel_receive:
            while True:
                message = await self.channel_receive()
                await self._on_message(message)

    async def _on_message(self, message: dict) -> None:
        service = message['service']
        payload = message['payload']
        await self.on_message(service, payload)

    async def on_message(self, service: str, message: dict) -> None:
        pass

    async def connect(self) -> None:
        IOLoop.current().add_callback(self.channel_receive_callback)
        self.channel_layer = get_channel_layer(alias='internal')
        if self.channel_layer is not None:
            self.channel_name = await self.channel_layer.new_channel(prefix=self.service.app.label)
            self.channel_receive = functools.partial(self.channel_layer.receive, self.channel_name)
            await self.channel_layer.group_add(
                self.channel_group_name(), self.channel_name)

    async def disconnect(self) -> None:
        await self.channel_layer.group_discard(
            self.channel_group_name(), self.channel_name)

    async def request(self, service: str, message: dict) -> None:
        try:
            await self.channel_layer.group_send(self.channel_group_name(service), message)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is not configured or doesn't support groups")

    def next_request_id(self, step=1):
        self._current_request_id += step
        return self._current_request_id

    async def request_for_response(self, service: str, message: dict) -> dict:
        future = Future()
        request_id = self.next_request_id()
        self._responses[request_id] = future
        await self.request(service, message)
        response = await future
        del self._responses[request_id]
        return response


class JSONRPCInternalConnection(InternalConnection):
    message_type = 'internal_json_rpc'

    def __init__(self, service, dispatcher=None):
        super().__init__(service)
        self.dispatcher = dispatcher if dispatcher is not None else Dispatcher()
        for method in api:
            self.dispatcher.add_method(method)

    async def on_message(self, service: str, message: dict) -> None:
        request_id = message.get('request_id')
        future = self._responses[request_id]
        if 'result' in message:
            result = message['result']
            future.set_result(result)
        else:  # must have a method
            try:
                json_rpc_request = JSONRPCRequest.from_json(message)
            except (TypeError, ValueError, JSONRPCInvalidRequestException):
                response = await JSONRPCResponseManager.handle(message, self.dispatcher)
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

            message = dict(payload=response, service=service, type=self.message_type)

            self.request(service, message)

from anthill.framework.handlers import JsonWebSocketHandler
from anthill.framework.core.jsonrpc.exceptions import JSONRPCInvalidRequestException
from anthill.framework.core.jsonrpc.jsonrpc import JSONRPCRequest
from anthill.framework.core.jsonrpc.manager import JSONRPCResponseManager
from anthill.framework.core.jsonrpc.utils import DatetimeDecimalEncoder
from anthill.framework.core.jsonrpc.dispatcher import Dispatcher
import logging
import copy


class JSONRPCMixin:
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store')

    async def json_rpc(self, message: str):
        try:
            json_rpc_request = JSONRPCRequest.from_json(message)
        except (TypeError, ValueError, JSONRPCInvalidRequestException):
            response = await JSONRPCResponseManager.handle(message, self.dispatcher)
        else:
            json_rpc_request.params = json_rpc_request.params or {}
            response = await JSONRPCResponseManager.handle_request(
                json_rpc_request, self.dispatcher)

        if response:
            response.serialize = self._serialize
            response = response.json

        return response

    def json_rpc_map(self):
        """Map of json-rpc available calls."""
        raise NotImplementedError


class WebSocketJSONRPCHandler(JSONRPCMixin, JsonWebSocketHandler):
    def __init__(self, application, request, dispatcher=None, **kwargs):
        super().__init__(application, request, **kwargs)
        self.dispatcher = dispatcher if dispatcher is not None else Dispatcher()

    async def on_message(self, message):
        """Handle incoming messages on the WebSocket."""
        result = await self.json_rpc(message)
        self.write_message(result)

    def json_rpc_map(self):
        return dict(
            (m_name, func.__doc__) for m_name, func
            in self.dispatcher.items()
        )

from anthill.platform.handlers.jsonrpc import JsonRPCSessionHandler, jsonrpc_method
from anthill.framework.auth.handlers import UserHandlerMixin


class SessionHandler(UserHandlerMixin, JsonRPCSessionHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(self, application, request, **kwargs)
        self.js_session = None

    def check_origin(self, origin):
        return True

    async def prepare(self):
        await super().prepare()
        # TODO: initialize

    async def open(self, *args, **kwargs):
        await super().open(*args, **kwargs)
        # TODO: open js_session

    async def close(self, code=None, reason=None):
        # TODO: cleanup js_session
        await super().close(code, reason)

    @jsonrpc_method()
    async def call(self, method_name, arguments):
        # TODO: make request to js_session
        pass

from v8py import JSException, JSPromise, Context, new, JavaScriptTerminated
from tornado.gen import with_timeout, TimeoutError, Future


CALL_TIMEOUT = 25


class JSSessionError(Exception):
    def __init__(self, code, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = code
        self.message = message


class JSSession:
    def __init__(self, build, instance):
        self.build = build
        self.instance = instance

    def call(self, method_name, args, timeout=CALL_TIMEOUT):
        context = self.build.context

        method = getattr(self.instance, method_name)

        try:
            future = context.async_call(method, (args,), JSFuture)
        except JSException as e:
            pass

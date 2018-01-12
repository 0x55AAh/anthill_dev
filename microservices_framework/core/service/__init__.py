from tornado.gen import coroutine
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from microservices_framework.apps.builder import app
from importlib import import_module
import signal
import logging


logger = logging.getLogger('app.server')


class BaseService(Application):
    name = None
    config = None
    server_class = HTTPServer

    def __init__(self, default_host=None, transforms=None, **kwargs):
        self.__class__.config = app.settings
        super(BaseService, self).__init__(self.get_handlers(), default_host, transforms, **kwargs)
        self._server = None
        self._socket = None
        self.setup()

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.name)

    def setup(self):
        self.__class__.name = app.name
        self.setup_server()

    def __sig_handler__(self, sig, frame):
        IOLoop.instance().add_callback(self.on_stop)

    def __sigpipe_handler__(self, sig, frame):
        pass

    def get_server(self):
        kwargs = self.get_server_kwargs() or {}
        return self.server_class(self, **kwargs)

    def get_server_kwargs(self):
        pass

    def get_handlers(self):
        routes_module = import_module(app.routes_conf)
        return getattr(routes_module, 'route_patterns', [])

    def setup_server(self):
        self._socket = app.socket
        self._server = self.get_server()
        self._server.listen(self._socket[1], self._socket[0])

        signal.signal(signal.SIGPIPE, self.__sigpipe_handler__)
        signal.signal(signal.SIGTERM, self.__sig_handler__)
        signal.signal(signal.SIGINT, self.__sig_handler__)

    def start(self):
        IOLoop.instance().add_callback(self.on_start)
        IOLoop.instance().start()

    def stop(self):
        if self._server:
            IOLoop.instance().add_callback(self.on_stop)
            self._server.stop()

    @coroutine
    def on_start(self):
        pass

    @coroutine
    def on_stop(self):
        pass

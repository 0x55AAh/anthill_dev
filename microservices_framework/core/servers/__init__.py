from tornado.gen import coroutine
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from microservices_framework.apps.builder import app
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
        self._server = self.get_server()

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
        return getattr(app.routes(), 'route_patterns', [])

    def setup_server(self, **kwargs):
        host = kwargs.pop('host')
        port = kwargs.pop('port')

        self._server.listen(port, host)

        signal.signal(signal.SIGPIPE, self.__sigpipe_handler__)
        signal.signal(signal.SIGTERM, self.__sig_handler__)
        signal.signal(signal.SIGINT, self.__sig_handler__)

    def start(self, **kwargs):
        self.setup_server(**kwargs)
        IOLoop.instance().add_callback(self.on_start)
        IOLoop.instance().start()

    def stop(self):
        if self._server:
            IOLoop.instance().add_callback(self.on_stop)
            self._server.stop()

    @coroutine
    def on_start(self):
        raise NotImplemented

    @coroutine
    def on_stop(self):
        raise NotImplemented

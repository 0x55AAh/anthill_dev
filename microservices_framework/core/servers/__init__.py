from tornado.web import Application as TornadoWebApplication
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from microservices_framework.apps import app
import signal
import logging


logger = logging.getLogger('app.server')


class BaseService(TornadoWebApplication):
    server_class = HTTPServer

    def __init__(self, handlers=None, default_host=None, transforms=None, **kwargs):
        kwargs.update(debug=app.debug)
        kwargs.update(compress_response=app.settings.COMPRESS_RESPONSE)
        kwargs.update(static_path=app.settings.STATIC_PATH)
        kwargs.update(static_url_prefix=app.settings.STATIC_URL)

        super(BaseService, self).__init__(handlers, default_host, transforms, **kwargs)

        self.config = app.settings
        self.name = app.name
        self.setup()

    def setup(self):
        """Setup server variables"""
        self.add_handlers(r'^(.*)$', app.routes)

        self.settings.update(cookie_secret=app.settings.SECRET_KEY)
        self.settings.update(xsrf_cookies=app.settings.CSRF_COOKIES)
        self.settings.update(template_path=app.settings.TEMPLATE_PATH)
        self.settings.update(login_url=app.settings.LOGIN_URL)

        self._load_ui_modules(app.ui_modules)
        self._load_ui_methods(app.ui_modules)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.name)

    def __sig_handler__(self, sig, frame):
        IOLoop.instance().add_callback(self.on_stop)

    def __sigpipe_handler__(self, sig, frame):
        ...

    @property
    def server(self):
        """Returns an instance of server class ``self.server_class``"""
        return self.server_class(self, **self.server_kwargs)

    @property
    def server_kwargs(self):
        """
        HTTPS supporting:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(os.path.join(data_dir, "mydomain.crt"),
                           os.path.join(data_dir, "mydomain.key"))
        if app.protocol == 'https':
            kwargs.update(ssl_options=ssl_ctx)
        """
        kwargs = {}
        return kwargs

    def setup_server(self, **kwargs):
        self.server.listen(app.port, app.host)

        signal.signal(signal.SIGPIPE, self.__sigpipe_handler__)
        signal.signal(signal.SIGTERM, self.__sig_handler__)
        signal.signal(signal.SIGINT, self.__sig_handler__)

    def start(self, **kwargs):
        """Start server"""
        self.setup_server(**kwargs)
        IOLoop.instance().add_callback(self.on_start)
        IOLoop.instance().start()

    def stop(self):
        """Stop server"""
        if self.server:
            IOLoop.instance().add_callback(self.on_stop)
            self.server.stop()

    async def on_start(self):
        raise NotImplementedError

    async def on_stop(self):
        raise NotImplementedError

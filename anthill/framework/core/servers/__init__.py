from tornado.web import Application as TornadoWebApplication
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
import signal
import logging

from anthill.framework.core.exceptions import ImproperlyConfigured

logger = logging.getLogger('anthill.server')


class BaseService(TornadoWebApplication):
    server_class = HTTPServer

    def __init__(self, handlers=None, default_host=None, transforms=None, app=None, **kwargs):
        kwargs.update(debug=app.debug)
        kwargs.update(compress_response=app.settings.COMPRESS_RESPONSE)
        kwargs.update(static_path=app.settings.STATIC_PATH)
        kwargs.update(static_url_prefix=app.settings.STATIC_URL)

        super(BaseService, self).__init__(handlers, default_host, transforms, **kwargs)

        self.config = app.settings
        self.app = app
        self.setup()

    def setup(self):
        """Setup server variables"""
        self.add_handlers(r'^(.*)$', self.app.routes)

        self.settings.update(cookie_secret=self.app.settings.SECRET_KEY)
        self.settings.update(xsrf_cookies=self.app.settings.CSRF_COOKIES)
        self.settings.update(template_path=self.app.settings.TEMPLATE_PATH)
        self.settings.update(login_url=self.app.settings.LOGIN_URL)

        self._load_ui_modules(self.app.ui_modules)
        self._load_ui_methods(self.app.ui_modules)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.app.name)

    def __sig_handler__(self, sig, frame):
        IOLoop.instance().add_callback(self.on_stop)

    def __sigpipe_handler__(self, sig, frame):
        pass

    @property
    def server(self):
        """Returns an instance of server class ``self.server_class``"""
        return self.server_class(self, **self.get_server_kwargs())

    def get_server_kwargs(self):
        kwargs = {}
        # HTTPS supporting
        https_config = getattr(self.config, 'HTTPS', None)
        if https_config is not None:
            import ssl
            key_file = https_config.get('key_file')
            crt_file = https_config.get('crt_file')
            if None in (key_file, crt_file):
                raise ImproperlyConfigured('Key or crt file not configured')
            ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_ctx.load_cert_chain(crt_file, key_file)
            kwargs.update(ssl_options=ssl_ctx)
            logger.debug('HTTPS is ON.')
        else:
            logger.warning('HTTPS not configured. May issue security problems.')
        return kwargs

    def setup_server(self, **kwargs):
        self.server.listen(self.app.port, self.app.host)

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

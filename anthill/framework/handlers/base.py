from tornado.web import (
    RequestHandler as BaseRequestHandler,
    StaticFileHandler as BaseStaticFileHandler
)
from tornado.websocket import WebSocketHandler as BaseWebSocketHandler
from anthill.framework.core.exceptions import ImproperlyConfigured
from anthill.framework.http import HttpGoneError
from anthill.framework.sessions.handlers import SessionHandlerMixin
from anthill.framework.utils.debug.report import ExceptionReporter
from anthill.framework.utils.format import bytes2human
from anthill.framework.utils.translation import default_locale
from anthill.framework.context_processors import build_context_from_context_processors
from anthill.framework.utils.module_loading import import_string
from anthill.framework.conf import settings
# noinspection PyProtectedMember
from tornado.httputil import _parse_header
import json
import logging


class TranslationHandlerMixin:
    # noinspection PyMethodMayBeStatic
    def get_user_locale(self):
        """
        Override to determine the locale from the authenticated user.
        If None is returned, we fall back to `get_browser_locale()`.
        This method should return a `tornado.locale.Locale` object,
        most likely obtained via a call like ``tornado.locale.get("en")``
        """
        return default_locale


class LogExceptionHandlerMixin:
    def log_exception(self, exc_type, exc_value, tb):
        # noinspection PyUnresolvedReferences
        super().log_exception(exc_type, exc_value, tb)
        logging.getLogger('anthill').exception(
            str(exc_value), extra={'handler': self})


class CommonRequestHandlerMixin:
    def clear(self):
        """Resets all headers and content for this response."""
        super().clear()
        if settings.HIDE_SERVER_VERSION:
            self.clear_header('Server')

    def is_secure(self):
        pass


class RequestHandler(TranslationHandlerMixin, LogExceptionHandlerMixin, SessionHandlerMixin,
                     CommonRequestHandlerMixin, BaseRequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.internal_request = self.application.internal_connection.request
        self.init_session()

    @property
    def config(self):
        """An alias for `self.application.config <Application.config>`."""
        return self.application.config

    def get_content_type(self):
        content_type = self.request.headers.get('Content-Type', 'text/plain')
        return _parse_header(content_type)

    def reverse_url(self, name, *args):
        url = super().reverse_url(name, *args)
        return url.rstrip('?')

    def get_current_user(self):
        """
        Override to determine the current user from, e.g., a cookie.
        This method may not be a coroutine.
        """
        return None

    def data_received(self, chunk):
        """
        Implement this method to handle streamed request data.
        Requires the `.stream_request_body` decorator.
        """

    def is_secure(self):
        return self.request.protocol in ('https',)

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    async def prepare(self):
        """Called at the beginning of a request before  `get`/`post`/etc."""
        self.setup_session()

    def finish(self, chunk=None):
        """Finishes this response, ending the HTTP request."""
        self.update_session()
        super().finish(chunk)

    def on_finish(self):
        """Called after the end of a request."""

    def set_default_headers(self):
        """
        Override this to set HTTP headers at the beginning of the request.
        """


class WebSocketHandler(TranslationHandlerMixin, LogExceptionHandlerMixin, CommonRequestHandlerMixin,
                       BaseWebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.settings.update(websocket_ping_interval=settings.WEBSOCKET_PING_INTERVAL)
        self.settings.update(websocket_ping_timeout=settings.WEBSOCKET_PING_TIMEOUT)
        self.settings.update(websocket_max_message_size=settings.WEBSOCKET_MAX_MESSAGE_SIZE)

    def on_message(self, message):
        """Handle incoming messages on the WebSocket."""
        raise NotImplementedError

    def data_received(self, chunk):
        """Implement this method to handle streamed request data."""

    def open(self, *args, **kwargs):
        """Invoked when a new WebSocket is opened."""

    def on_close(self):
        """Invoked when the WebSocket is closed."""

    def on_ping(self, data):
        """Invoked when the a ping frame is received."""

    def on_pong(self, data):
        """Invoked when the response to a ping frame is received."""

    def get_compression_options(self):
        if not settings.WEBSOCKET_COMPRESSION_LEVEL:
            return
        options = dict(compression_level=settings.WEBSOCKET_COMPRESSION_LEVEL)
        if settings.WEBSOCKET_MEM_LEVEL is not None:
            options.update(mem_level=settings.WEBSOCKET_MEM_LEVEL)
        return options


class JsonWebSocketHandler(WebSocketHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    def on_message(self, message):
        """Handle incoming messages on the WebSocket."""
        raise NotImplementedError


class JSONHandlerMixin:
    extra_context = None

    # noinspection PyUnresolvedReferences
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    # noinspection PyMethodMayBeStatic
    def dumps(self, data):
        return json.dumps(data)

    async def get_context_data(self, **kwargs):
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        return kwargs


class ContextMixin:
    """
    A default context mixin that passes the keyword arguments received by
    get_context_data() as the template context.
    """
    extra_context = None

    async def get_context_data(self, **kwargs):
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        # noinspection PyTypeChecker
        kwargs.update(await build_context_from_context_processors(self))
        return kwargs


class RedirectMixin:
    query_string = False
    handler_name = None
    url = None

    def initialize(self, query_string=None, handler_name=None, url=None):
        if query_string is not None:
            self.query_string = query_string
        if handler_name is not None:
            self.handler_name = handler_name
        if url is not None:
            self.url = url

    def get_redirect_url(self, *args, **kwargs):
        """
        Return the URL redirect to. Keyword arguments from the URL pattern
        match generating the redirect request are provided as kwargs to this
        method.
        """
        if self.url:
            url = self.url.format(*args)
        elif self.handler_name:
            try:
                from anthill.framework.utils.urls import reverse as reverse_url
                url = reverse_url(self.handler_name, *args, **kwargs)
            except KeyError:
                return
        else:
            return

        # noinspection PyUnresolvedReferences
        request_query = self.request.query
        if request_query and self.query_string:
            url = "%s?%s" % (url, request_query)
        return url


class TemplateMixin:
    """A mixin that can be used to render a template."""
    template_name = None

    def initialize(self, template_name=None):
        if template_name is not None:
            self.template_name = template_name

    def render(self, template_name=None, **kwargs):
        template_name = template_name or self.get_template_name()
        # noinspection PyUnresolvedReferences
        super().render(template_name, **kwargs)

    def get_template_namespace(self):
        from anthill.framework.apps import app
        # noinspection PyUnresolvedReferences
        namespace = super().get_template_namespace()
        namespace.update(app_version=app.version)
        namespace.update(debug=app.debug)
        namespace.update(bytes2human=bytes2human)
        return namespace

    def get_template_name(self):
        """Return a template name to be used for the request."""
        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_name()'")
        else:
            return self.template_name


class TemplateHandler(TemplateMixin, ContextMixin, RequestHandler):
    """
    Render a template. Pass keyword arguments to the context.
    """
    async def get(self, *args, **kwargs):
        context = await self.get_context_data(**kwargs)
        self.render(**context)

    def create_template_loader(self, template_path):
        """
        Returns a new template loader for the given path.

        May be overridden by subclasses. By default returns a
        directory-based loader on the given path, using the
        ``autoescape`` and ``template_whitespace`` application
        settings. If a ``template_loader`` application setting is
        supplied, uses that instead.
        """
        if "template_loader" in self.settings:
            return self.settings["template_loader"]
        kwargs = {}
        if "autoescape" in self.settings:
            # autoescape=None means "no escaping", so we have to be sure
            # to only pass this kwarg if the user asked for it.
            kwargs["autoescape"] = self.settings["autoescape"]
        if "template_whitespace" in self.settings:
            kwargs["whitespace"] = self.settings["template_whitespace"]
        template_loader_class = getattr(
            settings, "TEMPLATE_LOADER_CLASS", "anthill.framework.core.template.Loader")
        # ``session`` used for caching special template root.
        return import_string(template_loader_class)(
            template_path, session=self.session, **kwargs)

    def write_error(self, status_code, **kwargs):
        """
        Override to implement custom error pages.

        ``write_error`` may call `write`, `render`, `set_header`, etc
        to produce output as usual.

        If this error was caused by an uncaught exception (including
        HTTPError), an ``exc_info`` triple will be available as
        ``kwargs["exc_info"]``. Note that this exception may not be
        the "current" exception for purposes of methods like
        ``sys.exc_info()`` or ``traceback.format_exc``.
        """
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            self.set_header('Content-Type', 'text/plain')
            reporter = ExceptionReporter(self, exc_info=kwargs["exc_info"])
            self.finish(reporter.get_traceback_text())
        else:
            if status_code in range(500, 600):
                self.render("errors/500.html")
            elif status_code in range(400, 500):
                self.render("errors/404.html")
            else:
                self.render("errors/500.html")


class RedirectHandler(RedirectMixin, RequestHandler):
    """Provide a redirect on any GET request."""
    permanent = False

    async def get(self, *args, **kwargs):
        url = self.get_redirect_url(*args, **kwargs)
        if url:
            self.redirect(url, permanent=self.permanent)
        else:
            raise HttpGoneError

    async def head(self, *args, **kwargs):
        await self.get(*args, **kwargs)

    async def post(self, *args, **kwargs):
        await self.get(*args, **kwargs)

    async def options(self, *args, **kwargs):
        await self.get(*args, **kwargs)

    async def delete(self, *args, **kwargs):
        await self.get(*args, **kwargs)

    async def put(self, *args, **kwargs):
        await self.get(*args, **kwargs)

    async def patch(self, *args, **kwargs):
        await self.get(*args, **kwargs)


class JSONHandler(JSONHandlerMixin, RequestHandler):
    async def get(self, *args, **kwargs):
        context = await self.get_context_data(**kwargs)
        self.write(context)

    def write(self, data):
        super().write(self.dumps(data))


class StaticFileHandler(SessionHandlerMixin, BaseStaticFileHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.init_session()

    async def prepare(self):
        self.setup_session()
        # noinspection PyAttributeOutsideInit
        self.root = self.get_root()

    def get_root(self):
        """
        Returns static path dynamically retrieved from session storage.
        Adding ability to change ui theme directly from admin interface.
        """
        return self.session.get('static_path', self.root)

    def data_received(self, chunk):
        pass


class Handler404(TemplateHandler):
    template_name = 'errors/404.html'

    def prepare(self):
        self.set_status(404)
        self.render()

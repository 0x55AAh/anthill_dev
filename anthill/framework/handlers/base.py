from tornado.web import RequestHandler as BaseRequestHandler
from tornado.websocket import WebSocketHandler as BaseWebSocketHandler
from anthill.framework.core.exceptions import ImproperlyConfigured
from anthill.framework.http import HttpGoneError
from anthill.framework.utils.cache import patch_vary_headers
from anthill.framework.utils.format import bytes2human
from anthill.framework.utils.translation import default_locale
from anthill.framework.context_processors import build_context_from_context_processors
from anthill.framework.core.exceptions import SuspiciousOperation
from anthill.framework.sessions.backends.base import UpdateError
from anthill.framework.conf import settings
# noinspection PyProtectedMember
from tornado.httputil import _parse_header
from importlib import import_module
import json
import logging
import time


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


def _is_secure(request):
    return request.protocol in ('https', )


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


class RequestHandler(TranslationHandlerMixin, LogExceptionHandlerMixin, BaseRequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.internal_request = self.application.internal_connection.request
        # Setup SessionStore
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore

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

    def prepare(self):
        """Called at the beginning of a request before  `get`/`post`/etc."""
        session_key = self.get_cookie(settings.SESSION_COOKIE_NAME)
        self.request.session = self.SessionStore(session_key)
        setattr(self.request.__class__, 'is_secure', _is_secure)
        setattr(self.request.__class__, 'is_ajax', _is_ajax)

    def finish(self, chunk=None):
        """Finishes this response, ending the HTTP request."""
        # If request.session was modified, or if the configuration is to save the
        # session every time, save the changes and set a session cookie or delete
        # the session cookie if the session has been emptied.
        try:
            accessed = self.request.session.accessed
            modified = self.request.session.modified
            empty = self.request.session.is_empty()
        except AttributeError:
            pass
        else:
            # First check if we need to delete this cookie.
            # The session should be deleted only if the session is entirely empty
            if settings.SESSION_COOKIE_NAME in self.cookies and empty:
                self.clear_cookie(
                    settings.SESSION_COOKIE_NAME,
                    path=settings.SESSION_COOKIE_PATH,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                )
            else:
                if accessed:
                    patch_vary_headers(self._headers, ('Cookie',))
                if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                    if self.request.session.get_expire_at_browser_close():
                        max_age = None
                        expires = None
                    else:
                        max_age = self.request.session.get_expiry_age()
                        expires = time.time() + max_age
                    # Save the session data and refresh the client cookie.
                    # Skip session save for 500 responses.
                    if self._status_code != 500:
                        try:
                            self.request.session.save()
                        except UpdateError:
                            raise SuspiciousOperation(
                                "The request's session was deleted before the "
                                "request completed. The user may have logged "
                                "out in a concurrent request, for example."
                            )
                        self.set_cookie(
                            settings.SESSION_COOKIE_NAME,
                            self.request.session.session_key,
                            max_age=max_age,
                            expires=expires,
                            domain=settings.SESSION_COOKIE_DOMAIN,
                            path=settings.SESSION_COOKIE_PATH,
                            secure=settings.SESSION_COOKIE_SECURE or None,
                            httponly=settings.SESSION_COOKIE_HTTPONLY or None
                        )
        super().finish(chunk)

    def on_finish(self):
        """Called after the end of a request."""

    def clear(self):
        """Resets all headers and content for this response."""
        super().clear()
        if settings.HIDE_SERVER_VERSION:
            self.clear_header('Server')


class WebSocketHandler(TranslationHandlerMixin, LogExceptionHandlerMixin, BaseWebSocketHandler):
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

    def render(self, **kwargs):
        template_name = self.get_template_name()
        # noinspection PyUnresolvedReferences
        return super().render(template_name, **kwargs)

    def get_template_namespace(self):
        from anthill.framework.apps import app
        # noinspection PyUnresolvedReferences
        namespace = super().get_template_namespace()
        namespace.update(app_version=app.version)
        namespace.update(debug=app.debug)
        namespace.update(bytes2human=bytes2human)
        return namespace

    def get_template_name(self):
        """
        Return a template name to be used for the request.
        """
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
        return self.render(**context)


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

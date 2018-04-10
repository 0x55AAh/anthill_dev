from tornado.web import RequestHandler as BaseRequestHandler
from microservices_framework.core.exceptions import ImproperlyConfigured
from microservices_framework.utils.urls import reverse as reverse_url
from microservices_framework.http import HttpGoneError
from microservices_framework.apps import app


class RequestHandler(BaseRequestHandler):
    def reverse_url(self, name, *args):
        url = super(RequestHandler, self).reverse_url(name, *args)
        return url[:-1] if url.endswith('?') else url

    def data_received(self, chunk):
        pass


class ContextMixin:
    """
    A default context mixin that passes the keyword arguments received by
    get_context_data() as the template context.
    """
    extra_context = None

    def get_context_data(self, **kwargs):
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        return kwargs

    def get_template_namespace(self):
        from .context_processors import build_context_from_context_processors

        namespace = super(ContextMixin, self).get_template_namespace()
        namespace.update(build_context_from_context_processors(self))
        namespace.update(self.get_context_data(app_version=app.version))
        return namespace


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
                url = reverse_url(self.handler_name, *args, **kwargs)
            except KeyError:
                return None
        else:
            return None

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
        return super(TemplateMixin, self).render(template_name, **kwargs)

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
    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render(**context)


class RedirectHandler(RedirectMixin, RequestHandler):
    """Provide a redirect on any GET request."""
    permanent = False

    def get(self, *args, **kwargs):
        url = self.get_redirect_url(*args, **kwargs)
        if url:
            self.redirect(url, permanent=self.permanent)
        else:
            raise HttpGoneError

    def head(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def options(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.get(*args, **kwargs)

from tornado.web import RequestHandler, HTTPError
from microservices_framework.core.exceptions import ImproperlyConfigured
from microservices_framework.apps import app
from microservices_framework.utils.urls import reverse as reverse_url
from .context_processors import build_context_from_context_processors
from microservices_framework.http import HttpGoneError


class ContextMixin:
    """
    A default context mixin that passes the keyword arguments received by
    get_context_data() as the template context.
    """
    extra_context = None

    def get_context_data(self, **kwargs):
        kwargs.setdefault('reverse_url', reverse_url)
        kwargs.setdefault('app_version', app.version)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        kwargs.update(build_context_from_context_processors(self))
        return kwargs


class RedirectMixin:
    query_string = False
    pattern_name = None
    url = None

    def initialize(self, query_string=None, pattern_name=None, url=None):
        if query_string is not None:
            self.query_string = query_string
        if pattern_name is not None:
            self.pattern_name = pattern_name
        if url is not None:
            self.url = url

    def get_redirect_url(self, *args, **kwargs):
        """
        Return the URL redirect to. Keyword arguments from the URL pattern
        match generating the redirect request are provided as kwargs to this
        method.
        """
        if self.url:
            url = self.url % kwargs
        elif self.pattern_name:
            try:
                url = reverse_url(self.pattern_name, *args, **kwargs)
            except KeyError:
                return None
        else:
            return None

        request_query = self.request.query
        if request_query and self.query_string:
            url = "%s?%s" % (url, request_query)
        return url


class TemplateResponseMixin:
    """A mixin that can be used to render a template."""
    template_name = None

    def initialize(self, template_name=None):
        if template_name is not None:
            self.template_name = template_name

    def render(self, **kwargs):
        template_name = self.get_template_name()
        return super(TemplateResponseMixin, self).render(template_name, **kwargs)

    def get_template_name(self):
        """
        Return a template name to be used for the request.
        """
        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_name()'")
        else:
            return self.template_name


class TemplateHandler(TemplateResponseMixin, ContextMixin, RequestHandler):
    """
    Render a template. Pass keyword arguments to the context.
    """
    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render(**context)

    def data_received(self, chunk):
        pass


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

    def data_received(self, chunk):
        pass

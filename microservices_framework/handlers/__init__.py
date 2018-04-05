from tornado.web import RequestHandler
from microservices_framework.core.exceptions import ImproperlyConfigured
from microservices_framework.apps import app
from microservices_framework.utils.urls import reverse as reverse_url


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
        return kwargs


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

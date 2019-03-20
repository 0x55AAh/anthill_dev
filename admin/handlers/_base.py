from anthill.platform.api.internal import RequestTimeoutError, ServiceDoesNotExist, connector
from anthill.platform.auth.handlers import UserTemplateHandler
from anthill.framework.http.errors import HttpNotFoundError
from anthill.framework.core.exceptions import ImproperlyConfigured
import os


class ServiceContextMixin:
    """
    Put current request handler into special service context.
    Need for url kwarg `name` to identify target service.
    """
    service_name = None

    def initialize(self, service_name=None):
        if service_name is not None:
            self.service_name = service_name

    async def get_service_metadata(self):
        return await connector.internal_request(
            self.get_service_name(),
            method='get_service_metadata',
            registered_services=self.settings['registered_services'])

    def get_service_name(self):
        if self.service_name is None:
            raise ImproperlyConfigured(
                "ServiceContextMixin requires either a definition of "
                "'service_name' or an implementation of 'get_service_name()'")
        else:
            return self.service_name

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        try:
            metadata = await self.get_service_metadata()
        except RequestTimeoutError:
            pass  # ¯\_(ツ)_/¯
        except ServiceDoesNotExist:
            raise HttpNotFoundError
        else:
            context['metadata'] = metadata
        context['service_name'] = self.get_service_name()
        return context


class UserTemplateServiceRequestHandler(ServiceContextMixin, UserTemplateHandler):
    template_name = None

    def get_template_root(self):
        return os.path.join('services', self.get_service_name())

    def get_template_name(self):
        return os.path.join(self.get_template_root(), self.template_name)

    def render(self, template_name=None, **kwargs):
        try:
            super().render(template_name, **kwargs)
        except FileNotFoundError as e:
            kwargs.update(error=e)
            super().render(os.path.join('services', 'default.html'), **kwargs)


class PageHandlerMixin:
    page_name = None
    breadcrumbs = None
    template_root = ''

    def get_template_root(self):
        return self.template_root

    def get_template_name(self):
        return os.path.join(self.get_template_root(), self.page_name + '.html')

    def get_breadcrumbs(self):
        return self.breadcrumbs

    @property
    def extra_context(self):
        return {
            'page': self.page_name,
            'breadcrumbs': self.get_breadcrumbs(),
        }


class ServicePageHandler(PageHandlerMixin, UserTemplateServiceRequestHandler):
    def get_template_root(self):
        return os.path.join('services', self.get_service_name())

    def get_template_name(self):
        return os.path.join(self.get_template_root(), self.page_name + '.html')

from anthill.platform.api.internal import RequestTimeoutError, ServiceDoesNotExist, connector
from anthill.platform.auth.handlers import UserTemplateHandler
from anthill.framework.http.errors import HttpNotFoundError
import os


class ServiceContextMixin:
    """
    Put current request handler into special service context.
    Need for url kwarg `name` to identify target service.
    """

    async def get_service_metadata(self):
        return await connector.internal_request(
            self.path_kwargs['name'],
            method='get_service_metadata',
            registered_services=self.settings['registered_services'])

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
        return context


class UserTemplateServiceRequestHandler(ServiceContextMixin, UserTemplateHandler):
    template_name = None

    def get_template_name(self):
        return os.path.join(
            'services', self.path_kwargs['name'], self.template_name)

    def render(self, template_name=None, **kwargs):
        try:
            super().render(template_name, **kwargs)
        except FileNotFoundError:
            super().render(os.path.join('services', 'default.html'), **kwargs)


class PageHandlerMixin:
    page_name = None
    breadcrumbs = None

    def get_template_name(self):
        return '%s.html' % self.page_name

    def get_breadcrumbs(self):
        return self.breadcrumbs

    @property
    def extra_context(self):
        return {
            'page': self.page_name,
            'breadcrumbs': self.get_breadcrumbs(),
        }

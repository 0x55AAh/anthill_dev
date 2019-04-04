from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import DiscoveryServiceForm


class DiscoveryPageHandler(ServicePageHandler):
    service_name = 'discovery'


class DiscoveryFormHandler(FormMixin, ProcessFormMixin, DiscoveryPageHandler):
    pass


class IndexHandler(DiscoveryPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['services_list'] = self.settings['services_all_meta']
        return context


class ServiceDetail(DiscoveryFormHandler):
    page_name = 'service_detail'
    form_class = DiscoveryServiceForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        service_name = self.path_kwargs['service_name']
        context['service'] = {}  # TODO:
        return context

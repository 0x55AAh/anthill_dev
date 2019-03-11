from ._base import UserTemplateServiceRequestHandler, PageHandlerMixin


class ServicesList(UserTemplateServiceRequestHandler):
    template_name = 'index.html'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['services'] = self.settings['registered_services']
        return context


class ServiceDetail(UserTemplateServiceRequestHandler):
    template_name = 'service_detail.html'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context

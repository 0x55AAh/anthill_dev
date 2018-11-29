from admin.handlers._base import UserTemplateServiceRequestHandler


class ServicesList(UserTemplateServiceRequestHandler):
    template_name = 'services-list.html'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['services'] = self.settings['registered_services']
        return context


class ServiceDetail(UserTemplateServiceRequestHandler):
    template_name = 'service-detail.html'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context

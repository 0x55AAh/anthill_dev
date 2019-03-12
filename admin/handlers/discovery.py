from ._base import ServicePageHandler


class ServicesList(ServicePageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['services_all_meta'] = self.settings['services_all_meta']
        return context


class ServiceDetail(ServicePageHandler):
    page_name = 'service_detail'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context

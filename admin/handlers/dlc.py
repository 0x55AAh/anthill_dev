from ._base import ServicePageHandler


class DLCPageHandler(ServicePageHandler):
    service_name = 'dlc'


class IndexHandler(DLCPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['bundles_list'] = []  # TODO:
        return context

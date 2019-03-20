from ._base import ServicePageHandler


class ReportPageHandler(ServicePageHandler):
    service_name = 'report'


class IndexHandler(ReportPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['reports_list'] = []  # TODO:
        return context

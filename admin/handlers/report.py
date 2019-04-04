from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin


class ReportPageHandler(ServicePageHandler):
    service_name = 'report'


class ReportFormHandler(FormMixin, ProcessFormMixin, ReportPageHandler):
    pass


class IndexHandler(ReportPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['reports_list'] = []  # TODO:
        return context

from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import BackupForm


class BackupPageHandler(ServicePageHandler):
    service_name = 'backup'


class BackupFormHandler(FormMixin, ProcessFormMixin, BackupPageHandler):
    pass


class IndexHandler(BackupPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['backups_list'] = []  # TODO:
        return context

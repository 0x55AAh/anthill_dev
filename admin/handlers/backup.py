from ._base import ServicePageHandler


class BackupPageHandler(ServicePageHandler):
    service_name = 'backup'


class IndexHandler(BackupPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context

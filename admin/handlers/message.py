from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import MessageGroupForm


class MessagePageHandler(ServicePageHandler):
    service_name = 'message'


class MessageFormHandler(FormMixin, ProcessFormMixin, MessagePageHandler):
    pass


class IndexHandler(MessagePageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['groups_list'] = []  # TODO:
        return context


class GroupDetailHandler(MessagePageHandler):
    page_name = 'group_detail'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        group_id = self.path_kwargs['group_id']
        context['group'] = {}  # TODO:
        return context

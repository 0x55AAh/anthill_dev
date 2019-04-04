from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import ModerationForm


class ModerationPageHandler(ServicePageHandler):
    service_name = 'moderation'


class ModerationFormHandler(FormMixin, ProcessFormMixin, ModerationPageHandler):
    pass


class IndexHandler(ModerationPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['moderations_list'] = []  # TODO:
        return context


class ModerationDetailHandler(ModerationFormHandler):
    page_name = 'moderation_detail'
    form_class = ModerationForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        moderation_id = self.path_kwargs['moderation_id']
        context['moderation'] = {}  # TODO:
        return context

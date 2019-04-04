from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import BotForm


class BotPageHandler(ServicePageHandler):
    service_name = 'bot'


class BotFormHandler(FormMixin, ProcessFormMixin, BotPageHandler):
    pass


class IndexHandler(BotPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['bots_list'] = []  # TODO:
        return context


class BotDetailHandler(BotFormHandler):
    page_name = 'bot_detail'
    form_class = BotForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        bot_name = self.path_kwargs['bot_name']
        context['bot'] = {}  # TODO:
        return context


from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin


class LeaderboardPageHandler(ServicePageHandler):
    service_name = 'leaderboard'


class LeaderboardFormHandler(FormMixin, ProcessFormMixin, LeaderboardPageHandler):
    pass


class IndexHandler(LeaderboardPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['records_list'] = []  # TODO:
        return context

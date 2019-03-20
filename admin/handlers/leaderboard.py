from ._base import ServicePageHandler


class LeaderboardPageHandler(ServicePageHandler):
    service_name = 'leaderboard'


class IndexHandler(LeaderboardPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['records_list'] = []  # TODO:
        return context

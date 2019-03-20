from ._base import ServicePageHandler


class ProfilePageHandler(ServicePageHandler):
    service_name = 'profile'


class IndexHandler(ProfilePageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['profiles_list'] = []  # TODO:
        return context

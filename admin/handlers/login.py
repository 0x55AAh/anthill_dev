from ._base import ServicePageHandler


class LoginPageHandler(ServicePageHandler):
    service_name = 'login'


class IndexHandler(LoginPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['users_list'] = []  # TODO:
        return context

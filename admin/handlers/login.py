from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import UserForm


class LoginPageHandler(ServicePageHandler):
    service_name = 'login'


class LoginFormHandler(FormMixin, ProcessFormMixin, LoginPageHandler):
    pass


class IndexHandler(LoginPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['users_list'] = []  # TODO:
        return context


class UserDetailHandler(LoginFormHandler):
    page_name = 'user_detail'
    form_class = UserForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        user_id = self.path_kwargs['user_id']
        context['user'] = {}  # TODO:
        return context

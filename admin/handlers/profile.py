from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import ProfileForm


class ProfilePageHandler(ServicePageHandler):
    service_name = 'profile'


class ProfileFormHandler(FormMixin, ProcessFormMixin, ProfilePageHandler):
    pass


class IndexHandler(ProfilePageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['profiles_list'] = []  # TODO:
        return context


class ProfileDetailHandler(ProfileFormHandler):
    page_name = 'profile_detail'
    form_class = ProfileForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        profile_id = self.path_kwargs['profile_id']
        context['profile'] = {}  # TODO:
        return context

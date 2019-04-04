from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import (
    EnvironmentForm, EnvironmentApplicationForm, EnvironmentApplicationVersionForm
)


class EnvironmentPageHandler(ServicePageHandler):
    service_name = 'environment'


class EnvironmentFormHandler(FormMixin, ProcessFormMixin, EnvironmentPageHandler):
    pass


class IndexHandler(EnvironmentPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['environments_list'] = []  # TODO:
        return context


class EnvironmentDetailHandler(EnvironmentFormHandler):
    page_name = 'environment_detail'
    form_class = EnvironmentForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['environment'] = None  # TODO:
        return context


class ApplicationListHandler(EnvironmentPageHandler):
    page_name = 'application_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['applications_list'] = []  # TODO:
        return context


class ApplicationDetailHandler(EnvironmentFormHandler):
    page_name = 'application_detail'
    form_class = EnvironmentApplicationForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['application'] = None  # TODO:
        context['application_versions_list'] = []  # TODO:
        return context


class ApplicationVersionDetailHandler(EnvironmentFormHandler):
    page_name = 'application_version_detail'
    form_class = EnvironmentApplicationVersionForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['application_version'] = None  # TODO:
        return context

from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import (
    DLCBundleForm, DLCApplicationForm, DLCApplicationVersionForm,
    DLCDataVersionForm
)


class DLCPageHandler(ServicePageHandler):
    service_name = 'dlc'


class DLCFormHandler(FormMixin, ProcessFormMixin, DLCPageHandler):
    pass


class IndexHandler(DLCPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['bundles_list'] = []  # TODO:
        return context


class BundleDetailHandler(DLCFormHandler):
    page_name = 'bundle_detail'
    form_class = DLCBundleForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        bundle_id = self.path_kwargs['bundle_id']
        context['bundle'] = {}  # TODO:
        return context


class ApplicationListHandler(DLCPageHandler):
    page_name = 'application_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['applications_list'] = []  # TODO:
        return context


class ApplicationDetailHandler(DLCFormHandler):
    page_name = 'application_detail'
    form_class = DLCApplicationForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        application_id = self.path_kwargs['application_id']
        context['application'] = {}  # TODO:
        return context


class ApplicationVersionListHandler(DLCPageHandler):
    page_name = 'application_version_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['application_versions_list'] = []  # TODO:
        return context


class ApplicationVersionDetailHandler(DLCFormHandler):
    page_name = 'application_version_detail'
    form_class = DLCApplicationVersionForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        application_version_id = self.path_kwargs['application_version_id']
        context['application_version'] = {}  # TODO:
        return context


class DataVersionListHandler(DLCPageHandler):
    page_name = 'data_version_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['data_versions_list'] = []  # TODO:
        return context


class DataVersionDetailHandler(DLCFormHandler):
    page_name = 'data_version_detail'
    form_class = DLCDataVersionForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        data_version_id = self.path_kwargs['data_version_id']
        context['data_version'] = {}  # TODO:
        return context

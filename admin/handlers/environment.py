from ._base import ServicePageHandler


class EnvironmentPageHandler(ServicePageHandler):
    service_name = 'environment'


class IndexHandler(EnvironmentPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['environments_list'] = []  # TODO:
        return context


class EnvironmentDetailHandler(EnvironmentPageHandler):
    page_name = 'environment_detail'

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


class ApplicationDetailHandler(EnvironmentPageHandler):
    page_name = 'application_detail'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['application'] = None  # TODO:
        context['application_versions_list'] = []  # TODO:
        return context


class ApplicationVersionDetailHandler(EnvironmentPageHandler):
    page_name = 'application_version_detail'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['application_version'] = None  # TODO:
        return context

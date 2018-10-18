"""
Internal api methods for current service.

Example:

    from anthill.platform.api.internal import as_internal, InternalAPI

    @as_internal()
    async def your_internal_api_method(api: InternalAPI, *params, **options):
        # current_service = api.service
        ...
"""
from anthill.platform.api.internal import as_internal, InternalAPI
from anthill.framework.utils.urls import reverse, build_absolute_uri


@as_internal()
async def get_login_url(api: InternalAPI, **options):
    path = reverse('login')
    host_url = api.service.app.registry_entry['external']
    return build_absolute_uri(host_url, path)

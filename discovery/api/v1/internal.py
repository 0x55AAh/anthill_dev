"""
Internal api methods for current service.
Example:
    >>> from anthill.platform.api.internal import as_internal, InternalAPIError, InternalAPI
    >>>
    >>> @as_internal()
    >>> async def your_internal_api_method(api: InternalAPI, **kwargs):
    >>>    # current_service = api.service
    >>>    ...
"""
from anthill.platform.api.internal import as_internal, InternalAPIError, InternalAPI


@as_internal()
async def get_service(api: InternalAPI, name: str, network: str=None):
    result = await api.service.get_service(name, [network])
    return dict([result])


@as_internal()
async def set_service(api: InternalAPI, name: str, network: str, location: str):
    current_service = api.service

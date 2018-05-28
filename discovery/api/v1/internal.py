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
async def get_service(api: InternalAPI, service_name: str, network: str=None):
    current_service = api.service


@as_internal()
async def set_service(api: InternalAPI, service_name: str, network: str, location: str):
    current_service = api.service

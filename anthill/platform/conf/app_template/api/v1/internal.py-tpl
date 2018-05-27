"""
Internal api methods for current service.
Example:
    >>> from anthill.platform.api.internal import as_internal, InternalAPIError, InternalAPI
    >>>
    >>> @as_internal()
    >>> async def your_internal_api_method(api: InternalAPI, **kwargs):
    >>>    # service = api.service
    >>>    ...
"""
from anthill.platform.api.internal import as_internal, InternalAPIError, InternalAPI


@as_internal()
async def test(api: InternalAPI, **kwargs):
    return {'method': 'test', 'service': api.service.name}

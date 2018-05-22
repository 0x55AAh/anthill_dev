"""
Internal api methods for current service.
Example:
    >>> from anthill.platform.api.internal import as_internal, InternalAPIError, InternalAPI
    >>>
    >>> @as_internal()
    >>> async def your_internal_api_method(api: InternalAPI):
    >>>    # service = api.service
    >>>    pass
"""
from anthill.platform.api.internal import as_internal, InternalAPIError, InternalAPI

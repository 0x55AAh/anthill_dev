"""
Internal api methods for current service.
Example:
    >>> from anthill.platform.api.internal import as_internal, InternalAPI
    >>>
    >>> @as_internal()
    >>> async def your_internal_api_method(api: InternalAPI, **kwargs):
    >>>    # current_service = api.service
    >>>    ...
"""
from anthill.platform.api.internal import as_internal, InternalAPI
from login.models import User


@as_internal()
async def get_user(api: InternalAPI, user_id: str) -> User:
    user = User.query.filter_by(id=user_id).first()
    return user

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
from profile.models import Profile


@as_internal()
async def get_profile(api: InternalAPI, user_id: str) -> dict:
    profile = Profile.query.filter_by(user_id=user_id).first()
    try:
        return profile.dump.data
    except AttributeError:
        pass

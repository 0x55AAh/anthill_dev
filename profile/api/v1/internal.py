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
from anthill.framework.utils.asynchronous import thread_pool_exec as future_exec
from profile.models import Profile
from typing import Optional


@as_internal()
async def get_profile(api: InternalAPI, user_id: str, **options) -> Optional[dict]:
    query = Profile.query.filter_by(user_id=user_id)
    profile = await future_exec(query.one)
    return profile.dump()

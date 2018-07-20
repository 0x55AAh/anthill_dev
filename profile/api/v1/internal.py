"""
Internal api methods for current service.

Example:

from anthill.platform.api.internal import as_internal, InternalAPI

@as_internal()
async def your_internal_api_method(api: InternalAPI, **kwargs):
    # current_service = api.service
    ...
"""
from anthill.platform.api.internal import as_internal, InternalAPI
from profile.models import Profile


@as_internal()
async def get_profile(api: InternalAPI, user_id: str) -> dict:
    # ToDo: async query
    profile = Profile.query.filter_by(user_id=user_id).first()
    if profile is not None:
        return profile.dump().data


@as_internal()
async def get_profiles(api: InternalAPI, user_ids: list=None,
                       request=None, pagination: int=None, page: int=None) -> dict:
    # ToDo: async query
    if user_ids:
        profiles_query = Profile.query.filter(Profile.user_id.in_(user_ids))
    else:
        profiles_query = Profile.query

    pagination_kwargs = {
        'page': page,
        'per_page': pagination,
        'max_per_page': pagination
    }
    profiles = profiles_query.paginate(request, **pagination_kwargs)

    return {
        'data': Profile.Schema.dump(profiles.items).data
    }

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
from login.models import User


PAGINATED_BY = 50


@as_internal()
async def get_user(api: InternalAPI, user_id: str, include_profile: bool=False) -> dict:
    # ToDo: async query
    user = User.query.filter_by(id=user_id).first()
    if user is not None:
        data = user.dump().data
        if include_profile:
            data['profile'] = await user.get_profile()
        return data


@as_internal()
async def get_users(api: InternalAPI, request=None, include_profiles: bool=False,
                    pagination: int=PAGINATED_BY, page: int=None) -> dict:
    pagination_kwargs = {
        'page': page,
        'per_page': pagination,
        'max_per_page': pagination
    }
    users = User.query.paginate(request, **pagination_kwargs)  # ToDo: async query
    users_data = User.Schema.dump(users.items).data
    if include_profiles:
        profiles_data = await api.service.internal_connection.request(
            'profile', 'get_profiles', user_ids=[u['id'] for u in users_data])
        profiles_data_dict = {p['user_id']: p for p in profiles_data['data']}
        for user in users_data:
            user['profile'] = profiles_data_dict[user['id']]
    return {
        'data': users_data
    }

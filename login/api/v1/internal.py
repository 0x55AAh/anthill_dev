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
from anthill.framework.auth import authenticate as _authenticate, get_user_model


User = get_user_model()


PAGINATED_BY = 50


async def _get_user_data(user: User, include_profile: bool=False) -> dict:
    if user is not None:
        data = user.dump().data
        if include_profile:
            data['profile'] = await user.get_profile()
        return data


async def _get_user(user_id: str, include_profile: bool=False) -> dict:
    # ToDo: async query
    user = User.query.filter_by(id=user_id).first()
    return await _get_user_data(user, include_profile)


async def _get_users(request=None, include_profiles: bool=False,
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


@as_internal()
async def get_user(api: InternalAPI, user_id: str, include_profile: bool=False) -> dict:
    return await _get_user(user_id, include_profile)


@as_internal()
async def get_users(api: InternalAPI, request=None, include_profiles: bool=False,
                    pagination: int=PAGINATED_BY, page: int=None) -> dict:
    return await _get_users(request, include_profiles, pagination, page)


@as_internal()
async def authenticate(api: InternalAPI, **credentials) -> dict:
    # user = await _authenticate(request=None, **credentials)
    # data = await _get_user_data(user)
    # return data
    return {
        'id': 1,
        'username': 'woland',
        'is_active': True,
        'session_auth_hash': 'kukukuku',
        'backend': 'anthill.framework.auth.backends.ModelBackend'
    }


@as_internal()
async def login(api: InternalAPI, user_id: str) -> str:
    return '5s4df6s5d4f6sd54fsd6f54s'
    pass


@as_internal()
async def logout(api: InternalAPI, token: str) -> str:
    pass

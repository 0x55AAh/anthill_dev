"""
Internal api methods for current service.

Example:

    from anthill.platform.api.internal import as_internal, InternalAPI

    @as_internal()
    async def your_internal_api_method(api: InternalAPI, *params, **options):
        # current_service = api.service
        ...
"""
from anthill.platform.api.internal import as_internal, InternalAPI, connector
from anthill.framework.auth import authenticate as _authenticate, get_user_model
from anthill.framework.utils.asynchronous import thread_pool_exec
from anthill.framework.utils.urls import reverse, build_absolute_uri
from anthill.framework.core.exceptions import ObjectDoesNotExist
from typing import Optional
import functools

User = get_user_model()


def request_profile():
    return functools.partial(connector.internal_request, 'profile')


@as_internal()
async def get_user(api: InternalAPI, user_id: str, **options) -> Optional[dict]:
    query = User.query.filter_by(user_id=user_id)
    user = await future_exec(query.one)
    return user.dump()


@as_internal()
async def authenticate(api: InternalAPI, credentials: dict, **options) -> dict:
    user = await _authenticate(request=None, **credentials)
    if user is None:
        raise ObjectDoesNotExist
    return user.dump()


@as_internal()
async def logout(api: InternalAPI, token: str, **options) -> str:
    pass


@as_internal()
async def get_login_url(api: InternalAPI, **options) -> str:
    path = reverse('login')
    host_url = api.service.app.registry_entry['external']
    return build_absolute_uri(host_url, path)

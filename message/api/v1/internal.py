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
from anthill.framework.utils.urls import reverse, build_absolute_uri
from anthill.framework.conf import settings
from tornado.websocket import websocket_connect


async def send_message(api: InternalAPI, message, **kwargs):
    """Send message via local messenger."""

    path = reverse('messenger')
    host_url = api.service.app.registry_entry['external']
    url = build_absolute_uri(host_url, path)  # TODO: authentication token

    conn = await websocket_connect(url)
    await conn.write_message(message)
    response = await conn.read_message()

    conn.close()

    return response

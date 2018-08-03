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


@as_internal()
async def get_service(api: InternalAPI, name: str, network: str=None) -> dict:
    if network is not None:
        network = [network]
    result = await api.service.get_service(name, network)
    return {name: result}


@as_internal()
async def get_services(api: InternalAPI) -> dict:
    result = {}
    for name in await api.service.list_services():
        result[name] = await api.service.get_service(name)
    return result


@as_internal()
async def set_service(api: InternalAPI, name: str, network: str, location: str) -> None:
    await api.service.setup_service(name, {network: location})


@as_internal()
async def set_service_bulk(api: InternalAPI, name: str, networks: dict) -> None:
    await api.service.setup_service(name, networks)


@as_internal()
async def remove_service(api: InternalAPI, name: str) -> None:
    await api.service.remove_service(name)

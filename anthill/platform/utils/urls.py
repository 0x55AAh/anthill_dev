from anthill.platform.utils.internal_api import discovery_request


async def get_host_url(service: str, network: str='external') -> str:
    """Get host url by service name and network."""
    kwargs = dict(name=service, network=network)
    urls = await discovery_request(method='get_service', **kwargs)
    return urls[service].get(network)

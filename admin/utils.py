from anthill.platform.api.internal import RequestTimeoutError, connector


async def get_services_metadata(exclude_names=None):
    services_metadata = []
    exclude_names = exclude_names or []
    try:
        services_names = await connector.internal_request('discovery', method='get_services_names')
    except RequestTimeoutError:
        pass  # ¯\_(ツ)_/¯
    else:
        for name in services_names:
            if name in exclude_names:
                continue
            try:
                metadata = await connector.internal_request(name, method='get_service_metadata')
                services_metadata.append(metadata)
            except RequestTimeoutError:
                pass  # ¯\_(ツ)_/¯
    return services_metadata

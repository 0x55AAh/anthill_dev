from admin.ui.modules import MainSidebar
from anthill.platform.api.internal import RequestTimeoutError


async def main_sidebar(handler):
    main_sidebar_entries = []
    try:
        services = await handler.internal_request('discovery', method='get_services')
    except RequestTimeoutError:
        pass
    else:
        for name in services.keys():
            if name == handler.application.name:
                # Skip current application
                continue
            try:
                metadata = await handler.internal_request(name, method='get_service_metadata')
                kwargs = {
                    'title': metadata['title'],
                    'icon_class': metadata['icon_class']
                }
                entry = MainSidebar.Entry(**kwargs)
                main_sidebar_entries.append(entry)
            except RequestTimeoutError:
                pass
        main_sidebar_entries.sort()
    return {'main_sidebar_entries': main_sidebar_entries}

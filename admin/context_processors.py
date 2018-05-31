from admin.ui.modules import MainSidebar
from anthill.platform.api.internal import RequestTimeoutError


async def main_sidebar(handler):
    try:
        services = await handler.internal_request('discovery', method='get_services')
    except RequestTimeoutError:
        return {}
    else:
        main_sidebar_entries = []
        for name in services.keys():
            if name == handler.application.name:
                continue
            try:
                meta = await handler.internal_request(name, method='get_service_meta')
                kwargs = {
                    'title': meta['title'],
                    'icon_class': meta['icon_class']
                }
                entry = MainSidebar.Entry(**kwargs)
                main_sidebar_entries.append(entry)
            except RequestTimeoutError:
                pass
        return {
            'main_sidebar_entries': main_sidebar_entries
        }

from admin.services import AdminService
from admin.ui.modules import MainSidebar
from anthill.platform.api.internal import RequestTimeoutError

internal_api_connection_class = AdminService.internal_api_connection_class
internal_connection = internal_api_connection_class()
internal_request = internal_connection.request


async def main_sidebar(handler):
    try:
        services = await internal_request('discovery', method='get_services')
    except RequestTimeoutError:
        return {}
    else:
        main_sidebar_entries = []
        for name in services.keys():
            if name == handler.application.name:
                continue
            try:
                meta = await internal_request(name, method='get_service_meta')
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

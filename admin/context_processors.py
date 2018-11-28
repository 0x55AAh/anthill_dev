from admin.ui.modules import MainSidebar
from anthill.platform.api.internal import RequestTimeoutError, connector


async def main_sidebar(handler):
    main_sidebar_entries = []

    def make_entry(meta):
        kwargs = {
            'title': meta['title'],
            'icon_class': meta['icon_class'],
            'name': meta['name'],
        }
        entry = MainSidebar.Entry(**kwargs)
        main_sidebar_entries.append(entry)

    # Check for cached metatada
    if getattr(handler, 'metadata', None) and handler.metadata:
        for metadata in handler.metadata:
            make_entry(metadata)
    else:
        try:
            services = await connector.internal_request('discovery', method='get_services')
        except RequestTimeoutError:
            pass
        else:
            for name in services.keys():
                if name == handler.application.name:
                    # Skip current application
                    continue
                try:
                    metadata = await connector.internal_request(name, method='get_service_metadata')
                    make_entry(metadata)
                except RequestTimeoutError:
                    pass

    main_sidebar_entries.sort()

    return {
        'main_sidebar_entries': main_sidebar_entries,
        'main_sidebar_expanded': handler.session.get('sidebar-main-expanded', True),
    }

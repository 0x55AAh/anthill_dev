from admin.ui.modules import MainSidebar
from admin.utils import get_services_metadata


async def main_sidebar(handler):
    def build_entry(meta):
        kwargs = {
            'title': meta['title'],
            'icon_class': meta['icon_class'],
            'name': meta['name'],
        }
        return MainSidebar.Entry(**kwargs)

    # Check for cached metadata
    if getattr(handler, 'metadata', None):
        services_metadata = handler.metadata
    else:
        services_metadata = await get_services_metadata(exclude_names=[handler.application.name])

    main_sidebar_entries = list(map(build_entry, services_metadata))
    main_sidebar_entries.sort()

    return {
        'main_sidebar_entries': main_sidebar_entries,
        'main_sidebar_expanded': handler.session.get('sidebar-main-expanded', True),
    }

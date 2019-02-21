from admin.ui.modules import MainSidebar
from anthill.framework.apps import app


async def main_sidebar(handler):
    def build_entry(meta):
        keys = ('title', 'icon_class', 'name')
        kwargs = dict(map(lambda x: (x, meta[x]), keys))
        return MainSidebar.Entry(**kwargs)

    services_metadata = handler.settings['services_meta']
    main_sidebar_entries = sorted(map(build_entry, services_metadata))

    return {
        'main_sidebar_entries': main_sidebar_entries,
        'main_sidebar_expanded': handler.session.get('sidebar-main-expanded', True),
    }


async def additional_sidebar(handler):
    return {
        'has_detached_right': False,
    }


def metadata(handler):
    return {
        'admin_metadata': app.metadata
    }

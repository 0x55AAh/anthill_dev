from anthill.platform.services import PlainService, ControllerRole


class Service(PlainService, ControllerRole):
    """Anthill default service."""
    auto_register_on_discovery = False
    master = 'game_master'

    @staticmethod
    async def heartbeat_report(api, **options):
        pass

from anthill.platform.services import PlainService, ControllerRole


class Service(ControllerRole, PlainService):
    """Anthill default service."""
    master = 'game_master'

    @staticmethod
    async def heartbeat_report(api, **options):
        pass

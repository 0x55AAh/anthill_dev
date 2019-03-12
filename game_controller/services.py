from anthill.platform.services import PlainService, ControllerRole
from anthill.platform.api.internal import as_internal


class Service(ControllerRole, PlainService):
    """Anthill default service."""
    master = 'game_master'

    @staticmethod
    def setup_internal_api():
        @as_internal()
        async def heartbeat_report(api, **options):
            # TODO:
            pass

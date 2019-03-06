from anthill.platform.services import PlainService, MasterRole
from game_master.models import Server


class Service(PlainService, MasterRole):
    """Anthill default service."""
    controller = 'game_controller'

    async def heartbeat_callback(self, report):
        pass

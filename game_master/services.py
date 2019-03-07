from anthill.platform.services import PlainService, MasterRole
from anthill.framework.utils.asynchronous import as_future
from anthill.framework.core.cache import caches
from game_master.models import Server


class Service(MasterRole, PlainService):
    """Anthill default service."""

    @staticmethod
    @as_future
    def storage():
        return caches['controllers']

    async def heartbeat_callback(self, controller, report):
        pass

    async def controllers_registry(self):
        # TODO: get all controllers from database
        pass

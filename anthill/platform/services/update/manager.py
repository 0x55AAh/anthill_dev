from anthill.framework.conf import settings
from anthill.framework.utils.module_loading import import_string
from anthill.platform.services.update.exceptions import UpdateError
from anthill.framework.utils.asynchronous import as_future
from typing import Optional


UPDATES_SETTINGS = getattr(settings, 'UPDATES', {})
UPDATE_MANAGER = UPDATES_SETTINGS.get(
    'MANAGER', 'anthill.platform.services.update.backends.git.GitUpdateManager')


class UpdateManager:
    def __init__(self):
        self.manager = import_string(UPDATE_MANAGER)()

    async def update(self, version: Optional[str] = None):
        await self.update_system_requirements()
        await self.update_pip_requirements()
        await self.update_service(version)

    async def update_service(self, version):
        await self.manager.update(version)

    @as_future
    def update_pip_requirements(self):
        from pip import _internal
        _internal.main(['install', '-r', 'requirements.txt'])

    async def update_system_requirements(self):
        pass

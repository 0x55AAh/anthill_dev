from anthill.framework.conf import settings
from anthill.framework.utils.module_loading import import_string


UPDATES_SETTINGS = getattr(settings, 'UPDATES', {})
UPLOAD_BACKEND = UPDATES_SETTINGS.get('BACKEND', 'anthill.platform.services.update.backends.git.Backend')

backend = import_string(UPLOAD_BACKEND)


class UpdateManager:
    backend = backend

    async def versions(self):
        return self.backend.versions()

    async def current_version(self):
        pass

    async def check_updates(self):
        pass

    async def update(self, version=None):
        pass

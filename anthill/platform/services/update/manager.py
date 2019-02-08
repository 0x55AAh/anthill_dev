from anthill.framework.conf import settings
from anthill.framework.utils.module_loading import import_string


UPDATES_SETTINGS = getattr(settings, 'UPDATES', {})
UPDATES_BACKEND = UPDATES_SETTINGS.get(
    'BACKEND', 'anthill.platform.services.update.backends.git.Backend')

backend_class = import_string(UPDATES_BACKEND)


class UpdateManager:
    _backend = backend_class()

    def __getattr__(self, item):
        return getattr(self._backend, item)

from anthill.framework.conf import settings
from anthill.framework.utils.module_loading import import_string


UPDATES_SETTINGS = getattr(settings, 'UPDATES', {})
UPDATES_BACKEND = UPDATES_SETTINGS.get(
    'BACKEND', 'anthill.platform.services.update.backends.git.Backend')

UpdateManager = import_string(UPDATES_BACKEND)

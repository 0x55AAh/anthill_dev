from anthill.framework.conf import settings
from anthill.framework.utils.module_loading import import_string


UPDATES_SETTINGS = getattr(settings, 'UPDATES', {})
UPDATE_MANAGER = UPDATES_SETTINGS.get(
    'MANAGER', 'anthill.platform.services.update.backends.git.GitUpdateManager')

UpdateManager = import_string(UPDATE_MANAGER)

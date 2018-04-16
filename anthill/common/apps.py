from anthill.framework.apps.cls import Application
from anthill.framework.utils.module_loading import import_string
from functools import lru_cache
from .handlers import HealthControlHandler
from tornado.web import url


class BaseAnthillApplication(Application):
    """Base anthill application"""

    @lru_cache()
    def get_health_control_handler(self):
        if getattr(self.settings, 'HEALTH_CONTROL_HANDLER', None):
            handler = import_string(self.settings.HEALTH_CONTROL_HANDLER)
        else:
            handler = HealthControlHandler
        return handler

    @property
    @lru_cache()
    def routes(self):
        r = super(BaseAnthillApplication, self).routes
        if getattr(self.settings, 'HEALTH_CONTROL', False):
            r += [
                url(r'^/health/?$', self.get_health_control_handler(), name='health')
            ]
        return r

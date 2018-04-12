from anthill.framework.apps.cls import Application
from anthill.framework.utils.module_loading import import_string
from functools import lru_cache
from .handlers import MemoryControlHandler
from tornado.web import url


class BaseAnthillApplication(Application):
    """Base anthill application"""

    @lru_cache()
    def get_memory_control_handler(self):
        if getattr(self.settings, 'MEMORY_CONTROL_HANDLER', None):
            handler = import_string(self.settings.MEMORY_CONTROL_HANDLER)
        else:
            handler = MemoryControlHandler
        return handler

    @property
    @lru_cache()
    def routes(self):
        r = super(BaseAnthillApplication, self).routes
        if getattr(self.settings, 'MEMORY_CONTROL', False):
            r += [url(r'^/memory/?$', self.get_memory_control_handler(), name='memory')]
        return r

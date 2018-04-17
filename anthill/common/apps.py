from anthill.framework.apps.cls import Application
from functools import lru_cache
from .handlers import HealthControlHandler, MemoryDataTypesDetailHandler
from tornado.web import url


class BaseAnthillApplication(Application):
    """Base anthill application"""

    @property
    @lru_cache()
    def routes(self):
        r = super(BaseAnthillApplication, self).routes
        if getattr(self.settings, 'HEALTH_CONTROL', False):
            r += [
                url(r'^/health/?$', HealthControlHandler, name='health:index'),
                url(r'^/health/memory/data-types-detail/(.+)?$', MemoryDataTypesDetailHandler,
                    name='health:memory:data-types-detail'),
            ]
        return r

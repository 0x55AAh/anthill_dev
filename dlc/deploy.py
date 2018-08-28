from anthill.framework.conf import settings
from anthill.framework.utils.module_loading import import_string
from anthill.framework.core.exceptions import ImproperlyConfigured


METHODS = getattr(settings, 'DEPLOYMENT_METHODS', [])


class DeploymentMethod:
    name = None

    def __init__(self):
        if self.name is None:
            raise ImproperlyConfigured('Deployment method name is required')

    async def deploy(self, *args, **kwargs):
        raise NotImplementedError


class LocalDeploymentMethod(DeploymentMethod):
    name = 'local'

    async def deploy(self, *args, **kwargs):
        pass


class KeyCDNDeploymentMethod(DeploymentMethod):
    name = 'keycdn'

    async def deploy(self, *args, **kwargs):
        pass


class Deployment:
    methods = METHODS

    @property
    def _methods(self):
        return (import_string(m) for m in self.methods)

    @property
    def methods_dict(self):
        return {m.name: m for m in self._methods}

    def get_method(self, name):
        try:
            return self.methods_dict[name]
        except KeyError:
            raise ValueError('Deployment method `%s` is not supported.' % name)

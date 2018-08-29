from anthill.framework.conf import settings
from anthill.framework.utils.module_loading import import_string
from anthill.framework.core.exceptions import ImproperlyConfigured
from anthill.framework.utils.asynchronous import as_future
from anthill.framework.core.files.storage import default_storage
from anthill.platform.utils.ssh import PrivateSSHKeyContext
from anthill.platform.utils.rsync import Rsync
from dlc.exceptions import DeploymentError
from tornado.escape import to_unicode


METHODS = getattr(settings, 'DEPLOYMENT_METHODS', [])


class DeploymentMethod:
    name = None

    def __init__(self):
        if self.name is None:
            raise ImproperlyConfigured('Deployment method name is required')

    async def deploy(self, src: str, dst: str) -> str:
        raise NotImplementedError


class LocalDeploymentMethod(DeploymentMethod):
    """Stores files on local filesystem."""

    name = 'local'

    @as_future
    def deploy(self, src: str, dst: str) -> str:
        with open(src, 'rb') as src_f:
            default_storage.save(dst, src_f)
        return default_storage.url(dst)


class KeyCDNDeploymentMethod(DeploymentMethod):
    """Stores files on KeyCDN servers."""

    name = 'keycdn'
    hostname = 'rsync.keycdn.com'

    def __init__(self):
        super().__init__()
        self.username = None
        self.zone = None
        self.pri = None
        self.url = None

    async def deploy(self, src, dst):
        with PrivateSSHKeyContext(self.pri) as key_file:
            kwargs = {
                'identity_file': key_file,
                'hostname': self.hostname,
                'username': self.username,
                'src_path': src,
                'dst_path': dst
            }
            rsync = Rsync()
            rsync.configure(**kwargs)
            code, result, error = await rsync.upload()

            if code != 0:
                raise DeploymentError(code, to_unicode(error))


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

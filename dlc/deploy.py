from anthill.framework.conf import settings
from anthill.framework.utils.module_loading import import_string
from anthill.framework.utils.urls import build_absolute_uri
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
        raise NotImplementedError(
            'subclasses of DeploymentMethod must provide a deploy() method')

    def url(self, path: str) -> str:
        raise NotImplementedError(
            'subclasses of DeploymentMethod must provide a url() method')

    def configure(self, **kwargs):
        raise NotImplementedError(
            'subclasses of DeploymentMethod must provide a configure() method')


class LocalDeploymentMethod(DeploymentMethod):
    """Stores files on local filesystem."""

    name = 'local'

    def __init__(self):
        super().__init__()
        self.base_url = settings.LOCATION

    @as_future
    def deploy(self, src: str, dst: str) -> str:
        with open(src, 'rb') as src_f:
            default_storage.save(dst, src_f)
        return self.url(dst)

    def url(self, path: str) -> str:
        path = default_storage.url(path)
        return build_absolute_uri(self.base_url, path)

    def configure(self, **kwargs):
        pass


class KeyCDNDeploymentMethod(DeploymentMethod):
    """Stores files on KeyCDN servers."""

    name = 'keycdn'
    hostname = 'rsync.keycdn.com'

    def __init__(self, username=None, zone=None, key_data=None, base_url=None):
        super().__init__()
        self.username = username
        self.zone = zone
        self.key_data = key_data
        self.base_url = base_url

    def configure(self, username=None, zone=None, key_data=None, base_url=None):
        self.username = username
        self.zone = zone
        self.key_data = key_data
        self.base_url = base_url

    async def deploy(self, src: str, dst: str) -> str:
        with PrivateSSHKeyContext(self.key_data) as key_file:
            kwargs = {
                'identity_file': key_file,
                'hostname': self.hostname,
                'username': self.username,
                'src_path': src,
                'dst_path': dst
            }
            rsync = Rsync(**kwargs)
            code, _, error = await rsync.upload()

            if code != 0:
                raise DeploymentError(code, to_unicode(error))

            return self.url(dst)

    def url(self, path: str) -> str:
        return build_absolute_uri(self.base_url, path)


class Deployment:
    """Deployment methods switching class."""

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
            raise ValueError('Deployment method `%s` is not supported' % name)

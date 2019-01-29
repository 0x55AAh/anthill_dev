from anthill.platform.services import PlainService
from anthill.framework.auth.backends.manager import BackendManager as AuthBackendManager


class Service(PlainService):
    """Anthill default service."""

    def __init__(self, handlers=None, default_host=None, transforms=None, **kwargs):
        super().__init__(handlers, default_host, transforms, **kwargs)
        self.auth_manager = AuthBackendManager()

    async def set_login_url(self):
        self.settings.update(login_url=self.config.LOGIN_URL)

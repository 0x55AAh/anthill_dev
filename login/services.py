from anthill.platform.services import PlainService


class Service(PlainService):
    """Anthill default service."""

    async def set_login_url(self):
        self.settings.update(login_url=self.config.LOGIN_URL)

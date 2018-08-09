from anthill.platform.services import PlainService
from anthill.framework.auth.social.models import init_social


class Service(PlainService):
    """Anthill default service."""

    def setup(self):
        self.settings.update(social_auth_strategy=self.app.settings.SOCIAL_AUTH_STRATEGY)
        self.settings.update(social_auth_storage=self.app.settings.SOCIAL_AUTH_STORAGE)
        self.settings.update(authentication_backends=self.app.settings.AUTHENTICATION_BACKENDS)
        init_social(settings=self.settings)
        super().setup()

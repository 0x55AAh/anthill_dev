from anthill.framework.handlers import (
    RequestHandler,
    LoginHandlerMixin,
    LogoutHandlerMixin,
    UserHandlerMixin,
    AuthHandlerMixin
)
from anthill.framework.auth import authenticate


class UserRequestHandler(UserHandlerMixin, RequestHandler):
    """User aware RequestHandler."""

    async def prepare(self):
        await super().prepare()
        await self.setup_user()


class LoginHandler(LoginHandlerMixin, UserRequestHandler):
    async def post(self, *args, **kwargs):
        credentials = {}
        user = await authenticate(self.request, **credentials)
        self.login(user=user)


class LogoutHandler(LogoutHandlerMixin, UserRequestHandler):
    def post(self, *args, **kwargs):
        self.logout()


class RegisterHandler(RequestHandler):
    pass

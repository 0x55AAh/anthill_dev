from anthill.framework.handlers import (
    RequestHandler,
    LoginHandlerMixin,
    LogoutHandlerMixin,
    UserHandlerMixin,
    AuthHandlerMixin,
    UserRequestHandler
)
from anthill.framework.auth import authenticate


class LoginHandler(LoginHandlerMixin, UserRequestHandler):
    async def post(self, *args, **kwargs):
        credentials = self.get_credentials()
        user = await authenticate(self.request, **credentials)
        self.login(user=user)

    def get_credentials(self):
        field_names = ('username', 'password')
        return dict(map(lambda x: (x, self.get_argument(x)), field_names))


class LogoutHandler(LogoutHandlerMixin, UserRequestHandler):
    async def get(self, *args, **kwargs):
        await self.logout()

    async def post(self, *args, **kwargs):
        await self.get(*args, **kwargs)


class RegisterHandler(RequestHandler):
    pass

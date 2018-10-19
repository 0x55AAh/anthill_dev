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
        return {
            'username': self.get_argument('username'),
            'password': self.get_argument('password')
        }


class LogoutHandler(LogoutHandlerMixin, UserRequestHandler):
    async def get(self, *args, **kwargs):
        await self.logout()

    async def post(self, *args, **kwargs):
        await self.get(*args, **kwargs)


class RegisterHandler(RequestHandler):
    pass

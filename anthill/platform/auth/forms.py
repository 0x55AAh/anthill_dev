from anthill.framework.auth.forms import AuthenticationForm as BaseAuthenticationForm
from wtforms import StringField, PasswordField, validators, ValidationError
from anthill.framework.auth import authenticate
from tornado.util import ObjectDict


class AuthenticationForm(BaseAuthenticationForm):
    async def authenticate(self, request):
        user_data = {}  # ToDo: api request for user data
        user = ObjectDict(user_data)
        if not user:
            self.invalid_login_error()
        else:
            self.confirm_login_allowed(user)
        return user

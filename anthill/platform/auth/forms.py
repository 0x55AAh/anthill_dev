from anthill.framework.auth.forms import AuthenticationForm as BaseAuthenticationForm
from wtforms import ValidationError
from functools import partial


class AuthenticationForm(BaseAuthenticationForm):
    async def authenticate(self, internal_request):
        do_authenticate = partial(internal_request, 'login', 'authenticate')
        user = await do_authenticate(**self.get_credentials())  # User data dict
        print(user)
        if not user:
            self.invalid_login_error()
        else:
            self.confirm_login_allowed(user)
        return user

    # noinspection PyMethodMayBeStatic
    def confirm_login_allowed(self, user):
        if not user.get('is_active', False):
            raise ValidationError('Inactive user.')

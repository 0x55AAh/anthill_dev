from anthill.framework.forms import Form
from wtforms import StringField, PasswordField, validators, ValidationError
from anthill.framework.auth import authenticate


class AuthenticationForm(Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])

    async def authenticate(self, request):
        user = await authenticate(request, **self.get_credentials())
        if user is None:
            self.invalid_login_error()
        else:
            self.confirm_login_allowed(user)
        return user

    def get_credentials(self):
        return {
            'username': self.username.data,
            'password': self.password.data
        }

    # noinspection PyMethodMayBeStatic
    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a ``ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise ValidationError('Inactive user.')

    def invalid_login_error(self):
        raise ValidationError('Invalid user.')

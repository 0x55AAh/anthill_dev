from anthill.framework.forms import Form
from anthill.framework.utils.translation import translate as _
from wtforms import BooleanField, StringField, PasswordField, validators


class RegistrationForm(Form):
    username = StringField(_('Username'), [validators.DataRequired(), validators.Length(min=4, max=25)])
    email = StringField(_('Email'), [validators.DataRequired(), validators.Length(min=6, max=35)])
    password = PasswordField(_('Password'), [
        validators.DataRequired(),
        validators.EqualTo('confirm', message=_('Passwords must match'))
    ])
    confirm = PasswordField(_('Repeat Password'))
    accept_tos = BooleanField(_('I accept the TOS'), [validators.DataRequired()])


class LoginForm(Form):
    username = StringField(_('Username'), [validators.DataRequired(), validators.Length(min=4, max=25)])
    password = PasswordField(_('Password'), [validators.DataRequired()])


class PasswordResetForm(Form):
    email = StringField(_('Email'), [validators.Length(min=6, max=35)])


class UserForm(Form):
    pass

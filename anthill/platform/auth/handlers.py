from anthill.platform.auth.forms import AuthenticationForm
from anthill.framework.handlers.edit import FormHandler


class LoginHandlerMixin:
    async def login(self, user, backend=None):
        pass


class LoginHandler(LoginHandlerMixin, FormHandler):
    """
    Display the login form and handle the login action.
    """

    form_class = AuthenticationForm
    authentication_form = None
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'login.html'
    redirect_authenticated_user = False
    extra_context = None

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or self.reverse_url(settings.LOGIN_REDIRECT_URL)

    def get_redirect_url(self):
        """Return the user-originating redirect URL."""
        redirect_to = self.get_argument(
            self.redirect_field_name,
            self.get_query_argument(self.redirect_field_name, '')
        )
        return redirect_to

    def get_form_class(self):
        return self.authentication_form or self.form_class

    async def form_valid(self, form):
        """Security check complete. Log the user in."""
        user = await form.authenticate(self.request)
        await self.login(user)
        self.redirect(self.get_success_url())

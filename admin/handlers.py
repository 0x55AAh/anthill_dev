from microservices_framework.handlers import TemplateHandler, RedirectHandler
from .ui.modules import ServiceCard


class AuthenticatedHandlerMixin:
    access_token_key = 'access_token'

    def logout(self):
        self.clear_cookie(self.access_token_key)

    def get_current_user(self):
        if self.token is None:
            return None


class HomeHandler(TemplateHandler):
    template_name = 'index.html'
    extra_context = {
        'service_cards': [
            ServiceCard.Entry(title='Configuration', icon_class='icon-gear',
                              description='Configure your application dynamically', color='primary'),
            ServiceCard.Entry(title='Craft', icon_class='icon-hammer', description='Craft', color='danger'),
            ServiceCard.Entry(title='Discovery', icon_class='icon-direction',
                              description='Map each service location dynamically', color='success'),
            ServiceCard.Entry(title='DLC', icon_class='icon-cloud-download2',
                              description='Deliver downloadable content to the user', color='warning'),
            ServiceCard.Entry(title='Environment', icon_class='icon-cube',
                              description='Sandbox Test environment from Live', color='info'),
            ServiceCard.Entry(title='Events', icon_class='icon-calendar',
                              description='Compete the players with time-limited events', color='pink'),
            ServiceCard.Entry(title='Exec', icon_class='icon-circle-code',
                              description='Execute custom javascript code server-side', color='violet'),
            ServiceCard.Entry(title='Game', icon_class='icon-steam',
                              description='Manage game server instances', color='purple'),
            ServiceCard.Entry(title='Leader board', icon_class='icon-sort-numeric-asc',
                              description='See and edit player ranking', color='indigo'),
            ServiceCard.Entry(title='Login', icon_class='icon-key',
                              description='Manage user accounts, credentials and access tokens', color='blue'),
            ServiceCard.Entry(title='Market', icon_class='icon-basket', description='Market', color='teal'),
            ServiceCard.Entry(title='Messages', icon_class='icon-envelope',
                              description='Deliver messages from the user, to the user', color='green'),
            ServiceCard.Entry(title='Profiles', icon_class='icon-user',
                              description='Manage the profiles of the users', color='orange'),
            ServiceCard.Entry(title='Promo', icon_class='icon-gift',
                              description='Reward users with promo-codes', color='brown'),
            ServiceCard.Entry(title='Report', icon_class='icon-flag3',
                              description='User-submitted reports service', color='grey'),
            ServiceCard.Entry(title='Social', icon_class='icon-share3',
                              description='Manage social networks, groups and friend connections', color='slate'),
            ServiceCard.Entry(title='Store', icon_class='icon-cart',
                              description='In-App Purchasing, with server validation', color='primary'),
        ]
    }

    def get_context_data(self, **kwargs):
        context = super(HomeHandler, self).get_context_data(**kwargs)
        return context


class LoginHandler(TemplateHandler):
    template_name = 'login.html'

    def post(self, *args, **kwargs):
        pass

    def get_context_data(self, **kwargs):
        context = super(LoginHandler, self).get_context_data(**kwargs)
        return context


class LogoutHandler(AuthenticatedHandlerMixin, RedirectHandler):
    handler_name = 'login'

    def get(self, *args, **kwargs):
        self.logout()
        return super(LogoutHandler, self).get(*args, **kwargs)


class DebugHandler(TemplateHandler):
    template_name = 'debug.html'

    def get_context_data(self, **kwargs):
        context = super(DebugHandler, self).get_context_data(**kwargs)
        return context

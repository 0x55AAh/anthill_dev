from anthill.framework.handlers import TemplateHandler, RedirectHandler, WebSocketHandler
from .ui.modules import ServiceCard
from anthill.framework.core.channels.layers import get_channel_layer
from anthill.framework.core.channels.exceptions import InvalidChannelLayerError
import functools
import json


class AuthenticatedHandlerMixin:
    access_token_key = 'access_token'

    async def logout(self):
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

    async def get_context_data(self, **kwargs):
        context = await super(HomeHandler, self).get_context_data(**kwargs)
        return context


class LoginHandler(TemplateHandler):
    template_name = 'login.html'

    async def post(self, *args, **kwargs):
        pass

    async def get_context_data(self, **kwargs):
        context = await super(LoginHandler, self).get_context_data(**kwargs)
        return context


class LogoutHandler(AuthenticatedHandlerMixin, RedirectHandler):
    handler_name = 'login'

    async def get(self, *args, **kwargs):
        await self.logout()
        await super(LogoutHandler, self).get(*args, **kwargs)


class DebugHandler(TemplateHandler):
    template_name = 'debug.html'

    async def get_context_data(self, **kwargs):
        context = await super(DebugHandler, self).get_context_data(**kwargs)
        return context


class TestWSHandler(WebSocketHandler):
    groups = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.channel_layer = None
        self.channel_name = None
        self.channel_receive = None

        if self.groups is None:
            self.groups = []

    async def open(self, *args, **kwargs):
        """Invoked when a new WebSocket is opened."""
        # Initialize channel layer
        self.channel_layer = get_channel_layer()
        if self.channel_layer is not None:
            self.channel_name = await self.channel_layer.new_channel()
            self.channel_receive = functools.partial(self.channel_layer.receive, self.channel_name)
        # Add channel groups
        try:
            for group in self.groups:
                await self.channel_layer.group_add(group, self.channel_name)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is not configured or doesn't support groups")

    async def send(self, message, binary=False, close=None):
        self.write_message(message, binary=binary)
        # await self.channel_layer.send(self.channel_name, message)
        if close:
            await self.close(close)

    async def receive(self, message):
        print(message)

    async def on_message(self, message):
        # message = await self.channel_receive()
        await self.receive(message)

    async def on_connection_close(self):
        # Remove channel groups
        try:
            for group in self.groups:
                await self.channel_layer.group_discard(group, self.channel_name)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is not configured or doesn't support groups")
        super().on_connection_close()

    def on_close(self):
        """Invoked when the WebSocket is closed."""


class TestJWSHandler(TestWSHandler):
    async def send_json(self, message, close=None):
        """
        Encode the given message as JSON and send it to the client.
        """
        await super().send(
            message=await self.encode_json(message),
            close=close
        )

    async def receive(self, message):
        """
        Decode JSON message to dict and pass it to receive_json method.
        """
        if message:
            await self.receive_json(await self.decode_json(text_data))
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

    async def receive_json(self, message):
        pass

    @classmethod
    async def decode_json(cls, text_data):
        return json.loads(text_data)

    @classmethod
    async def encode_json(cls, content):
        return json.dumps(content)

from anthill.framework.handlers import (
    TemplateHandler, RedirectHandler, WebSocketJSONRPCHandler
)
from anthill.platform.auth.handlers import LoginHandler as BaseLoginHandler
from anthill.platform.core.messenger.handlers import MessengerHandler
from anthill.platform.core.messenger.client import BaseClient
from anthill.platform.api.internal import RequestTimeoutError, is_response_valid
from admin.ui.modules import ServiceCard
from anthill.framework.handlers import UploadFileStreamHandler
from anthill.framework.utils.cache import cached_method
import logging


logger = logging.getLogger('anthill.application')


class AuthenticatedHandlerMixin:
    access_token_key = 'access_token'

    async def logout(self):
        self.clear_cookie(self.access_token_key)

    def get_current_user(self):
        if self.token is None:
            return None


class HomeHandler(TemplateHandler):
    template_name = 'index.html'

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.metadata = []

    # @cached_method(timeout=300)
    async def get(self, *args, **kwargs):
        await super().get(*args, **kwargs)

    async def get_metadata(self, services):
        res = []
        for name in services.keys():
            if name == self.application.name:
                # Skip current application
                continue
            try:
                metadata = await self.internal_request(name, method='get_service_metadata')
            except RequestTimeoutError:
                pass
            else:
                res.append(metadata)
        res.sort(key=lambda x: x['title'])
        return res

    async def get_context_data(self, **kwargs):
        service_cards = []
        try:
            services = await self.internal_request('discovery', method='get_services')
        except RequestTimeoutError:
            pass
        else:
            if is_response_valid(services):
                self.metadata = await self.get_metadata(services)
                for metadata in self.metadata:
                    card = ServiceCard.Entry(**metadata)
                    service_cards.append(card)
        kwargs.update(service_cards=service_cards)
        context = await super().get_context_data(**kwargs)
        return context


class LoginHandler(BaseLoginHandler):
    pass


class LogoutHandler(AuthenticatedHandlerMixin, RedirectHandler):
    handler_name = 'login'

    async def get(self, *args, **kwargs):
        await self.logout()
        await super().get(*args, **kwargs)


class DebugHandler(TemplateHandler):
    template_name = 'debug.html'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        return context


class User:
    def __init__(self, _id):
        self.id = _id


class Client(BaseClient):
    def get_user_serialized(self):
        pass

    async def get_friends(self, id_only=False):
        pass

    async def get_groups(self):
        pass

    async def create_group(self, group_name, group_data):
        pass

    async def delete_group(self, group_name):
        pass

    async def update_group(self, group_name, group_data):
        pass

    async def join_group(self, group_name):
        pass

    async def leave_group(self, group_name):
        pass

    async def enumerate_group(self, group, new=None):
        pass

    async def create_message(self, group, message):
        pass

    async def get_messages(self, group, message_ids):
        pass

    async def delete_messages(self, group, message_ids):
        pass

    async def update_messages(self, group, messages_data):
        pass

    async def read_messages(self, group, message_ids):
        pass

    async def forward_messages(self, group, message_ids, group_to):
        pass


class TestMessengerHandler(MessengerHandler):
    client_class = Client

    def get_client_instance(self):
        return self.client_class(user=User(1))


class TestWSJSONRPCHandler(WebSocketJSONRPCHandler):
    pass

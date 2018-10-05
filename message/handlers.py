from anthill.platform.core.messenger import client, handlers
from anthill.platform.auth import RemoteUser


class Client(client.BaseClient):
    async def authenticate(self, user=None) -> None:
        """
        While authentication process we need to update `self.user`.
        Raise AuthenticationFailedError if failed.
        """
        if user is not None:
            # noinspection PyAttributeOutsideInit
            self.user = user

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


class MessengerHandler(handlers.MessengerHandler):
    client_class = Client

    def get_client_instance(self):
        from datetime import datetime
        return self.client_class(
            user=RemoteUser(
                '1',
                username='test',
                password='1234',
                created=datetime.now(),
                last_login=datetime.now()
            )
        )

from anthill.framework.auth.models import AnonymousUser
from anthill.platform.core.messenger.exceptions import NotAuthenticatedError
from anthill.platform.core.messenger.settings import messenger_settings
from anthill.platform.auth import RemoteUser
from typing import Optional


def create_personal_group(user_identifier) -> str:
    return '.'.join([messenger_settings.PERSONAL_GROUP_PREFIX, str(user_identifier)])


class BaseClient:
    user_id_key = 'id'

    def __init__(self, user: Optional[RemoteUser] = None):
        self.user = user or AnonymousUser()

    async def authenticate(self, user: Optional[RemoteUser] = None) -> None:
        """
        While authentication process we need to update `self.user`.
        """
        if user is not None:
            self.user = user
        if isinstance(self.user, (type(None), AnonymousUser)):
            raise NotAuthenticatedError

    def create_personal_group(self, user_id: Optional[str] = None) -> str:
        func = messenger_settings.PERSONAL_GROUP_FUNCTION
        return func(user_id or self.get_user_id())

    def get_user_id(self) -> str:
        return getattr(self.user, self.user_id_key)

    def get_user_serialized(self) -> dict:
        raise NotImplementedError

    async def get_friends(self, id_only: bool = False) -> list:
        raise NotImplementedError

    async def get_groups(self) -> list:
        raise NotImplementedError

    async def create_group(self, group_name: str, group_data: dict) -> str:
        raise NotImplementedError

    async def delete_group(self, group_name: str) -> None:
        raise NotImplementedError

    async def update_group(self, group_name: str, group_data: dict) -> None:
        raise NotImplementedError

    async def join_group(self, group_name: str) -> None:
        raise NotImplementedError

    async def leave_group(self, group_name: str) -> None:
        raise NotImplementedError

    async def enumerate_group(self, group: str, new=None) -> list:
        """
        List messages received from group.
        :param group: Group identifier
        :param new: Shows what messages deeded.
                    Get all messages if `None`,
                        new (not read) messages if `True`,
                        old (read) messages if `False`.
        :return: Serialized messages list
        """
        raise NotImplementedError

    async def create_message(self, group: str, message: dict) -> str:
        """
        Save message on database.
        :param group: Group identifier
        :param message: Message data
        :return: Message identifier
        """
        raise NotImplementedError

    async def get_messages(self, group: str, message_ids: list) -> list:
        """
        Get messages list by id
        :param group: Group identifier
        :param message_ids: message id list
        :return: Serialized messages list
        """
        raise NotImplementedError

    async def delete_messages(self, group: str, message_ids: list):
        """

        :param group:
        :param message_ids:
        :return:
        """
        raise NotImplementedError

    async def update_messages(self, group: str, messages_data: dict):
        """

        :param group:
        :param messages_data:
        :return:
        """
        raise NotImplementedError

    async def read_messages(self, group: str, message_ids: list):
        """

        :param group:
        :param message_ids:
        :return:
        """
        raise NotImplementedError

    def __eq__(self, other):
        return self.user == other.user

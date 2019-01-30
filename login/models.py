# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.auth.base_models import AbstractUser
from anthill.platform.api.internal import InternalAPIMixin
from anthill.platform.core.messenger.message import send_message
from anthill.platform.core.messenger.settings import messenger_settings


class User(InternalAPIMixin, AbstractUser):
    __tablename__ = 'user'

    async def get_profile(self):
        return await self.internal_request('profile', 'get_profile', user_id=self.id)

    async def send_message(self, message, callback=None, client=None):
        """Send a message to this user."""
        create_personal_group = messenger_settings.PERSONAL_GROUP_FUNCTION
        data = {
            'data': message,
            'group': create_personal_group(self.id),
            'trusted': True
        }
        await send_message(
            event='create_message',
            data=data,
            callback=callback,
            client=client
        )

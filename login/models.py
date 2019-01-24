# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.auth.base_models import AbstractUser
from anthill.platform.api.internal import InternalAPIMixin


class User(InternalAPIMixin, AbstractUser):
    __tablename__ = 'user'

    async def get_profile(self):
        return await self.internal_request('profile', 'get_profile', user_id=self.id)

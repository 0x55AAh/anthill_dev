# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.auth.base_models import AbstractUser


class User(AbstractUser):
    __tablename__ = 'users'

    async def get_profile(self):
        from anthill.platform.utils.internal_api import internal_request
        return await internal_request('profile', 'get_profile', user_id=self.id)
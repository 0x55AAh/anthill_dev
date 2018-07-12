# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.auth.models import User as BaseUser
from anthill.platform.utils.internal_api import internal_request


class User(BaseUser):
    async def get_profile(self):
        return await internal_request('profile', 'get_profile', user_id=self.id)

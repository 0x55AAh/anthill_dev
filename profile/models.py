# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.platform.api.internal import InternalAPIMixin
from sqlalchemy_utils.types.json import JSONType


class Profile(InternalAPIMixin, db.Model):
    """Extra fields for User model."""
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    payload = db.Column(JSONType, nullable=False, default={})

    async def get_user(self):
        return await self.internal_request('login', 'get_user', user_id=self.user_id)

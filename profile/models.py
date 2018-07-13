# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db


class Profile(db.Model):
    """Extra fields for User model."""
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    payload = db.Column(db.JSON, nullable=False, default={})

    @classmethod
    def __declare_last__(cls):
        """Validation must be here."""

    async def get_user(self):
        from anthill.platform.utils.internal_api import internal_request
        return await internal_request('login', 'get_user', user_id=self.user_id)



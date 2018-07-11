# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db


class Profile(db.Model):
    """Extra fields for User model."""

    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    payload = db.Column(db.JSON)

    @classmethod
    def __declare_last__(cls):
        """Validation must be here."""

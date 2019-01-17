# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db


class ModerationAction(db.Model):
    __tablename__ = 'moderation_actions'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    reason = db.Column(db.String(512), nullable=False)

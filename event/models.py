# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.platform.api.internal import InternalAPIMixin
from sqlalchemy_utils.types.json import JSONType
import enum


@enum.unique
class EventOnFinishActions(enum.Enum):
    pass


@enum.unique
class EventParticipationStatus(enum.Enum):
    pass


class Event(db.Model):
    __tablename__ = 'events'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False, default=timezone.now)
    finish_at = db.Column(db.DateTime, nullable=False)
    payload = db.Column(JSONType, nullable=False, default={})
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    on_finish = db.Column(db.Enum(EventOnFinishActions))


class EventCategory(db.Model):
    __tablename__ = 'event_categories'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(512), nullable=False)
    payload = db.Column(JSONType, nullable=False, default={})


class EventParticipation(InternalAPIMixin, db.Model):
    __tablename__ = 'events'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False, default=timezone.now)
    status = db.Column(db.Enum(EventParticipationStatus))
    payload = db.Column(JSONType, nullable=False, default={})
    user_id = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, nullable=False)

    async def get_user(self):
        return await self.internal_request('login', 'get_user', user_id=self.user_id)


class EventGenerator(db.Model):
    __tablename__ = 'event_generators'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pool_id = db.Column(db.Integer)


class EventGeneratorPool(db.Model):
    __tablename__ = 'event_generator_pools'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

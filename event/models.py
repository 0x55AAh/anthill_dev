# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.platform.api.internal import InternalAPIMixin
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.uuid import UUIDType
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.event import listens_for
from celery.worker.control import revoke
from typing import Optional
from datetime import timedelta
import enum


@enum.unique
class EventParticipationStatus(enum.Enum):
    pass


class Event(db.Model):
    __tablename__ = 'events'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False, default=timezone.now)
    start_at = db.Column(db.DateTime, nullable=False)
    finish_at = db.Column(db.DateTime, nullable=False)
    payload = db.Column(JSONType, nullable=False, default={})
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    on_start_task_id = db.Column(UUIDType(binary=False))
    on_finish_task_id = db.Column(UUIDType(binary=False))

    @hybrid_property
    def active(self) -> bool:
        return self.finish_at > timezone.now() >= self.on_start() and self.is_active

    @hybrid_property
    def started(self) -> bool:
        return self.start_at >= timezone.now()

    @hybrid_property
    def finished(self) -> bool:
        return self.finish_at < timezone.now()

    @hybrid_property
    def start_in(self) -> Optional[timedelta]:
        if self.start_at >= timezone.now():
            return self.start_at - timezone.now()

    @hybrid_property
    def finish_in(self) -> Optional[timedelta]:
        if self.finish_at >= timezone.now():
            return self.finish_at - timezone.now()

    async def on_start(self) -> None:
        pass

    async def on_finish(self) -> None:
        pass


@listens_for(Event, 'after_insert')
def on_event_create(mapper, connection, target):
    from event import tasks

    if target.start_in:
        task = tasks.on_event_start.apply_async(
            [target.id], countdown=target.start_in.seconds)
        target.on_start_task_id = task.id

    if target.finish_in:
        task = tasks.on_event_finish.apply_async(
            [target.id], countdown=target.finish_in.seconds)
        target.on_finish_task_id = task.id


@listens_for(Event, 'after_update')
def on_event_update(mapper, connection, target):
    from event import tasks
    from anthill.platform.core.celery import app

    if target.on_start_task_id:
        revoke(app, target.on_start_task_id)
    if target.on_finish_task_id:
        revoke(app, target.on_finish_task_id)

    if target.start_in:
        task = tasks.on_event_start.apply_async(
            [target.id], countdown=target.start_in.seconds)
        target.on_start_task_id = task.id

    if target.finish_in:
        task = tasks.on_event_finish.apply_async(
            [target.id], countdown=target.finish_in.seconds)
        target.on_finish_task_id = task.id


@listens_for(Event, 'after_delete')
def on_event_delete(mapper, connection, target):
    from anthill.platform.core.celery import app

    if target.on_start_task_id:
        revoke(app, target.on_start_task_id)
    if target.on_finish_task_id:
        revoke(app, target.on_finish_task_id)


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

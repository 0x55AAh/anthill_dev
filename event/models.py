# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.framework.utils.translation import translate as _
from anthill.framework.utils.asynchronous import as_future
from anthill.platform.api.internal import InternalAPIMixin
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.uuid import UUIDType
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.event import listens_for
from celery.worker.control import revoke
from anthill.platform.core.celery import app as celery_app
from tornado.ioloop import IOLoop
from typing import Optional
from datetime import timedelta
import marshmallow_sqlalchemy as ma
import enum
import logging


logger = logging.getLogger('anthill.application')


@enum.unique
class EventParticipationStatus(enum.Enum):
    JOINED = 0
    LEAVED = 1


@enum.unique
class EventStatus(enum.Enum):
    STARTED = 0
    FINISHED = 1


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('event_categories.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=timezone.now)
    start_at = db.Column(db.DateTime, nullable=False)
    finish_at = db.Column(db.DateTime, nullable=False)
    payload = db.Column(JSONType, nullable=False, default={})
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    on_start_task_id = db.Column(UUIDType(binary=False))
    on_finish_task_id = db.Column(UUIDType(binary=False))

    participations = db.relationship('EventParticipation', backref='event')

    @classmethod
    def _schema(cls):
        class Meta:
            model = cls
            fields = ('id', 'finish_at', 'payload')

        return type('Schema', (ma.ModelSchema,), {'Meta': Meta})

    Schema = _schema

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

    def dumps(self):
        return self.Schema().dump(self).data

    async def on_start(self) -> None:
        # TODO: bulk get_users request
        for p in self.participations:
            user = await p.get_user()
            msg = {
                'type': EventStatus.STARTED.name,
                'data': self.dumps()
            }
            await user.send_message(msg)

    async def on_finish(self) -> None:
        # TODO: bulk get_users request
        for p in self.participations:
            user = await p.get_user()
            msg = {
                'type': EventStatus.FINISHED.name,
                'data': self.dumps()
            }
            await user.send_message(msg)

    @as_future
    def join(self, user_id):
        kwargs = dict(
            user_id=user_id,
            event_id=self.id,
            status=EventParticipationStatus.JOINED.name
        )
        EventParticipation.create(**kwargs)

    @as_future
    def leave(self, user_id):
        kwargs = dict(
            user_id=user_id,
            event_id=self.id,
            status=EventParticipationStatus.LEAVED.name
        )
        p = EventParticipation.query.filter_by(**kwargs).first()
        if p is not None:
            p.status = 'LEAVED'
            p.save()
        else:
            logger.warning('User (%s) is not joined to event (%s), '
                           'so cannot leave.' % (user_id, self.id))


@listens_for(Event, 'after_insert')
def on_event_create(mapper, connection, target):
    from event import tasks

    if not target.is_active:
        return

    if target.start_in:
        task = tasks.on_event_start.apply_async(
            (target.id,), countdown=target.start_in.seconds)
        target.on_start_task_id = task.id

    if target.finish_in:
        task = tasks.on_event_finish.apply_async(
            (target.id,), countdown=target.finish_in.seconds)
        target.on_finish_task_id = task.id


@listens_for(Event, 'after_update')
def on_event_update(mapper, connection, target):
    from event import tasks

    if target.on_start_task_id:
        revoke(celery_app, target.on_start_task_id)
    if target.on_finish_task_id:
        revoke(celery_app, target.on_finish_task_id)

    if not target.is_active:
        return

    if target.start_in:
        task = tasks.on_event_start.apply_async(
            (target.id,), countdown=target.start_in.seconds)
        target.on_start_task_id = task.id

    if target.finish_in:
        task = tasks.on_event_finish.apply_async(
            (target.id,), countdown=target.finish_in.seconds)
        target.on_finish_task_id = task.id


@listens_for(Event, 'after_delete')
def on_event_delete(mapper, connection, target):
    if target.on_start_task_id:
        revoke(celery_app, target.on_start_task_id)
    if target.on_finish_task_id:
        revoke(celery_app, target.on_finish_task_id)


class EventCategory(db.Model):
    __tablename__ = 'event_categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(512), nullable=False)
    payload = db.Column(JSONType, nullable=False, default={})
    events = db.relationship('Event', backref='event')


class EventParticipation(InternalAPIMixin, db.Model):
    __tablename__ = 'event_participations'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False, default=timezone.now)
    status = db.Column(db.Enum(EventParticipationStatus))
    payload = db.Column(JSONType, nullable=False, default={})
    user_id = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    async def on_status_changed(self):
        user = await self.get_user()
        msg = {
            'type': 'STATUS_CHANGED',
            'status': self.status
        }
        await user.send_message(msg)

    async def get_user(self):
        return await self.internal_request('login', 'get_user', user_id=self.user_id)


@listens_for(EventParticipation.status, 'set', active_history=True)
def on_event_participation_status_changed(target, value, oldvalue, initiator):
    if value != oldvalue:
        IOLoop.current().add_callback(target.on_status_changed)


class EventGenerator(db.Model):
    __tablename__ = 'event_generators'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pool_id = db.Column(db.Integer, db.ForeignKey('event_generator_pools.id'))


class EventGeneratorPool(db.Model):
    __tablename__ = 'event_generator_pools'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    generators = db.relationship('EventGenerator', backref='pool')

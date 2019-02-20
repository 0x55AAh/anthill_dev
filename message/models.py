# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.platform.api.internal import InternalAPIMixin
from anthill.framework.utils.translation import translate_lazy as _
from anthill.framework.utils.asynchronous import as_future
from sqlalchemy_utils.types.choice import ChoiceType
from anthill.platform.auth import RemoteUser
from functools import partial


MESSAGE_STATUSES = (
    ('new', _('New')),
    ('read', _('Read')),
)

GROUP_TYPES = (
    ('p', _('Personal')),
    ('m', _('Multiple')),
    ('c', _('Channel')),
)


class MessageStatus(InternalAPIMixin, db.Model):
    __tablename__ = 'message_statuses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(ChoiceType(MESSAGE_STATUSES), default='new')
    updated = db.Column(db.DateTime, onupdate=timezone.now)
    receiver_id = db.Column(db.Integer)

    @property
    def request_user(self):
        return partial(self.internal_request, 'login', 'get_user')

    async def get_receiver(self) -> RemoteUser:
        return await self.request_user(user_id=self.receiver_id, include_profile=False)


class BaseMessage(InternalAPIMixin, db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=timezone.now)
    updated = db.Column(db.DateTime, onupdate=timezone.now)
    active = db.Column(db.Boolean, nullable=False, default=True)
    draft = db.Column(db.Boolean, nullable=False, default=False)
    content_type = db.Column(db.String(512), nullable=False, default='text/plain')
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

    @property
    def request_user(self):
        return partial(self.internal_request, 'login', 'get_user')

    async def get_sender(self) -> RemoteUser:
        return await self.request_user(user_id=self.sender_id, include_profile=False)

    @classmethod
    @as_future
    def outgoing_messages(cls, sender_id):
        return cls.query.filter_by(active=True, sender_id=sender_id)

    @classmethod
    @as_future
    def incoming_messages(cls, receiver_id):
        pass

    @classmethod
    async def draft_messages(cls, sender_id):
        return await cls.outgoing_messages(sender_id).filter_by(draft=True)

    @classmethod
    @as_future
    def new_messages(cls, receiver_id):
        pass


class Message(BaseMessage):
    __tablename__ = 'messages'


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    type = db.Column(ChoiceType(GROUP_TYPES))
    created = db.Column(db.DateTime, default=timezone.now)
    updated = db.Column(db.DateTime, onupdate=timezone.now)
    active = db.Column(db.Boolean, nullable=False, default=True)
    messages = db.relationship('Message', backref='group')

    def get_messages(self):
        return self.messages.filter_by(active=True).all()

# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.platform.api.internal import InternalAPIMixin
from anthill.framework.utils.translation import translate_lazy as _
from anthill.framework.utils.asynchronous import as_future
from sqlalchemy_utils.types import ChoiceType, URLType
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
    message_id = db.Column(
        db.Integer, db.ForeignKey('messages.id', ondelete='CASCADE'))
    receiver_id = db.Column(db.Integer)

    @property
    def request_user(self):
        return partial(self.internal_request, 'login', 'get_user')

    async def get_receiver(self) -> RemoteUser:
        return await self.request_user(user_id=self.receiver_id, include_profile=False)


class Message(InternalAPIMixin, db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=timezone.now)
    updated = db.Column(db.DateTime, onupdate=timezone.now)
    active = db.Column(db.Boolean, nullable=False, default=True)
    draft = db.Column(db.Boolean, nullable=False, default=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    status = db.relationship('MessageStatus', backref='message', uselist=False)
    disc = db.Column(db.String)

    __mapper_args__ = {
        'polymorphic_on': disc,
        'polymorphic_identity': 'message',
    }

    @property
    def request_user(self):
        return partial(self.internal_request, 'login', 'get_user')

    async def get_sender(self) -> RemoteUser:
        return await self.request_user(user_id=self.sender_id, include_profile=False)

    @classmethod
    @as_future
    def outgoing_messages(cls, sender_id, **kwargs):
        return cls.query.filter_by(active=True, sender_id=sender_id, **kwargs)

    @classmethod
    @as_future
    def incoming_messages(cls, receiver_id, **kwargs):
        return cls.query.filter_by(active=True, **kwargs).filter(cls.status.receiver_id == receiver_id)

    @classmethod
    async def draft_messages(cls, sender_id, **kwargs):
        return await cls.outgoing_messages(sender_id).filter_by(draft=True, **kwargs)

    @classmethod
    @as_future
    def new_messages(cls, receiver_id, **kwargs):
        return cls.query.filter_by(active=True, **kwargs).filter(cls.status.receiver_id == receiver_id and
                                                                 cls.status.value == 'new')


class TextMessage(Message):
    __tablename__ = 'text_messages'

    id = db.Column(db.Integer, db.ForeignKey('messages.id'), primary_key=True)
    content_type = db.Column(db.String(128), nullable=False, default='text/plain')
    value = db.Column(db.Text, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'text_message',
    }


class FileMessage(Message):
    __tablename__ = 'file_messages'

    id = db.Column(db.Integer, db.ForeignKey('messages.id'), primary_key=True)
    content_type = db.Column(db.String(128), nullable=False)
    value = db.Column(URLType, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'file_message',
    }


class URLMessage(Message):
    __tablename__ = 'url_messages'

    id = db.Column(db.Integer, db.ForeignKey('messages.id'), primary_key=True)
    content_type = db.Column(db.String(128), nullable=False)
    value = db.Column(URLType, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'url_message',
    }


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    type = db.Column(ChoiceType(GROUP_TYPES))
    created = db.Column(db.DateTime, default=timezone.now)
    updated = db.Column(db.DateTime, onupdate=timezone.now)
    active = db.Column(db.Boolean, nullable=False, default=True)
    messages = db.relationship('Message', backref='group', lazy='dynamic')

    @as_future
    def get_messages(self, user_id=None, **kwargs):
        default_kwargs = dict(active=True)
        if user_id is not None:
            default_kwargs.update(sender_id=user_id)
        default_kwargs.update(kwargs)
        return self.messages.filter_by(**default_kwargs)

    @as_future
    def get_memberships(self, user_id=None, **kwargs):
        default_kwargs = dict(active=True)
        if user_id is not None:
            default_kwargs.update(user_id=user_id)
        default_kwargs.update(kwargs)
        return self.memberships.filter_by(**default_kwargs)


class GroupMembership(db.Model):
    __tablename__ = 'groups_memberships'

    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=timezone.now)
    active = db.Column(db.Boolean, nullable=False, default=True)
    group = db.relationship('Group', backref=db.backref('memberships', lazy='dynamic'))


def get_friends(user_id):
    # TODO:
    # groups = Group.query.filter_by(active=True, type='p').filter(GroupMembership.group)
    pass


def make_friends(user_id1, user_id2):
    # TODO:
    pass


def remove_friends(user_id1, user_id2):
    # TODO:
    pass

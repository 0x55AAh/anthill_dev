# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.platform.api.internal import InternalAPIMixin
from anthill.framework.utils.asynchronous import as_future
from anthill.framework.core.mail.asynchronous import send_mail
from anthill.platform.auth import RemoteUser
from sqlalchemy_utils.types.json import JSONType
from anthill.framework.utils import timezone
from typing import Optional
from datetime import timedelta
import enum


DEFAULT_MODERATION_WARNING_THRESHOLD = 3


@enum.unique
class ActionType(enum.Enum):
    BAN_ACCOUNT = 'ban_account'
    HIDE_MESSAGE = 'hide_message'


@enum.unique
class ActionReasons(enum.Enum):
    pass


class BaseModerationAction(InternalAPIMixin, db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action_type = db.Column(db.Enum(ActionType), nullable=False)
    moderator_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=timezone.now)
    reason = db.Column(db.Enum(ActionReasons), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    extra_data = db.Column(JSONType, nullable=False, default={})

    async def get_user(self) -> RemoteUser:
        return await self.internal_request(
            'login', 'get_user', user_id=self.user_id, include_profile=False)

    async def get_moderator(self) -> RemoteUser:
        return await self.internal_request(
            'login', 'get_user', user_id=self.moderator_id, include_profile=False)

    @as_future
    def turn_on(self, commit: bool = False) -> None:
        self.is_active = True
        self.save(commit)

    @as_future
    def turn_off(self, commit: bool = False) -> None:
        self.is_active = False
        self.save(commit)

    def active(self) -> bool:
        return self.is_active


class ModerationAction(BaseModerationAction):
    __tablename__ = 'actions'
    __table_args__ = ()

    finish_at = db.Column(db.DateTime)

    def time_limited(self) -> bool:
        return self.finish_at is not None

    def finish_in(self) -> Optional[timedelta]:
        if self.time_limited():
            return self.finish_at - timezone.now()

    def finished(self) -> Optional[bool]:
        if self.time_limited():
            return self.finish_at <= timezone.now()

    def active(self) -> bool:
        if self.time_limited():
            return self.is_active and not self.finished()
        return self.is_active

    @classmethod
    async def moderate(cls, action_type, reason, moderator, user, extra_data=None):
        obj = cls.create(
            action_type=action_type,
            reason=reason,
            moderator_id=moderator.id,
            user_id=user.id,
            extra_data=extra_data
        )
        # TODO: send message to user (user.send_message)
        # TODO: send email to user (user.send_mail)
        return obj


class ModerationWarning(BaseModerationAction):
    __tablename__ = 'warnings'
    __table_args__ = ()

    @classmethod
    async def warn(cls, action_type, reason, moderator, user, extra_data=None):
        obj = cls.create(
            action_type=action_type,
            reason=reason,
            moderator_id=moderator.id,
            user_id=user.id,
            extra_data=extra_data
        )
        # TODO: send message to user (user.send_message)
        # TODO: send email to user (user.send_mail)
        # TODO: check for warns count and trigger moderation action if counter exceeded
        # await cls.moderate(action_type, reason, moderator, user, extra_data)
        return obj


class ModerationWarningThreshold(db.Model):
    __tablename__ = 'warning_thresholds'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action_type = db.Column(db.Enum(ActionType), nullable=False)
    value = db.Column(
        db.Integer, nullable=False, default=DEFAULT_MODERATION_WARNING_THRESHOLD)

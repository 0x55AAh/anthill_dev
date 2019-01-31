# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.framework.utils.asynchronous import as_future
from anthill.framework.utils.translation import translate as _
from anthill.platform.api.internal import InternalAPIMixin
from anthill.platform.auth import RemoteUser
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils.types.json import JSONType
from datetime import timedelta
from functools import partial
from typing import Optional
import enum


DEFAULT_MODERATION_WARNING_THRESHOLD = 3


@enum.unique
class ActionType(enum.Enum):
    BAN_ACCOUNT = 0
    HIDE_MESSAGE = 1


class BaseModerationAction(InternalAPIMixin, db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action_type = db.Column(db.Enum(ActionType), nullable=False)
    moderator_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=timezone.now)
    reason = db.Column(db.String(512), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    extra_data = db.Column(JSONType, nullable=False, default={})

    def __init__(self, **kwargs):  # for IDE inspection
        super().__init__(**kwargs)

    @property
    def request_user(self):
        return partial(self.internal_request, 'login', 'get_user')

    async def get_user(self) -> RemoteUser:
        return await self.request_user(user_id=self.user_id, include_profile=False)

    async def get_moderator(self) -> RemoteUser:
        return await self.request_user(user_id=self.moderator_id, include_profile=False)

    @as_future
    def turn_on(self, commit: bool = False) -> None:
        """Set action in active state."""
        self.is_active = True
        self.save(commit)

    @as_future
    def turn_off(self, commit: bool = False) -> None:
        """Set action in inactive state."""
        self.is_active = False
        self.save(commit)

    @hybrid_property
    def active(self) -> bool:
        return self.is_active

    @classmethod
    async def actions_query(cls, user_id: str, **filters) -> db.Query:
        """Get actions query for current user id."""
        return cls.query.filter_by(active=True, user_id=user_id, **filters)

    @staticmethod
    async def send_email(user: RemoteUser, subject, message, from_email=None, **kwargs):
        await user.send_mail(subject, message, from_email, **kwargs)

    @staticmethod
    async def send_message(user: RemoteUser, message):
        await user.send_message(message)


class ModerationAction(BaseModerationAction):
    __tablename__ = 'actions'
    __table_args__ = ()

    finish_at = db.Column(db.DateTime)

    @hybrid_property
    def time_limited(self) -> bool:
        return self.finish_at is not None

    def finish_in(self) -> Optional[timedelta]:
        if self.time_limited:
            return self.finish_at - timezone.now()

    @hybrid_property
    def finished(self) -> bool:
        if self.time_limited:
            return self.finish_at <= timezone.now()
        return True

    @hybrid_property
    def active(self) -> bool:
        return self.is_active and not self.finished

    @classmethod
    async def moderate(cls, action_type: str, reason: str,
                       moderator: RemoteUser, user: RemoteUser,
                       extra_data: Optional[dict] = None, finish_at=None,
                       commit=True):
        data = dict(
            action_type=action_type,
            reason=reason,
            moderator_id=moderator.id,
            user_id=user.id,
            finish_at=finish_at,
            extra_data=extra_data
        )
        obj = cls(**data)
        db.session.add(obj)
        if commit:
            db.session.commit()

        await send_email(
            user,
            subject=_('You are moderated'),
            message=reason,
            from_email=None,     # TODO:
            fail_silently=False,
            html_message=None    # TODO:
        )
        await send_message(user, message=reason)


class ModerationWarning(BaseModerationAction):
    __tablename__ = 'warnings'
    __table_args__ = ()

    @property
    def threshold_model(self):
        return ModerationWarningThreshold

    @classmethod
    async def warn(cls, action_type: str, reason: str,
                   moderator: RemoteUser, user: RemoteUser,
                   finish_at=None, extra_data: Optional[dict] = None):
        data = dict(
            action_type=action_type,
            reason=reason,
            moderator_id=moderator.id,
            user_id=user.id,
            extra_data=extra_data
        )
        obj = cls(**data)
        db.session.add(obj)

        try:
            warns_count = await cls.actions_query(user.id, action_type=action_type).count()
            threshold = cls.threshold_model.query.filter_by(action_type=action_type).first()
            if warns_count >= threshold.value:
                await cls.moderate(action_type, reason, moderator, user, extra_data,
                                   finish_at, commit=False)
            else:
                await send_email(
                    user,
                    subject=_('You are warned'),
                    message=reason,
                    from_email=None,     # TODO:
                    fail_silently=False,
                    html_message=None    # TODO:
                )
                await send_message(user, message=reason)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise


class ModerationWarningThreshold(db.Model):
    __tablename__ = 'warning_thresholds'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action_type = db.Column(db.Enum(ActionType), unique=True, nullable=False)
    value = db.Column(db.Integer, nullable=False,
                      default=DEFAULT_MODERATION_WARNING_THRESHOLD)

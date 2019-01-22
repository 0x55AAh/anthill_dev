# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.platform.api.internal import InternalAPIMixin
from anthill.platform.auth import RemoteUser
from sqlalchemy_utils.types.json import JSONType
from anthill.framework.utils import timezone
from typing import Optional
from datetime import timedelta
import enum


@enum.unique
class ActionType(enum.Enum):
    BAN_ACCOUNT = 'ban_account'
    HIDE_MESSAGE = 'hide_message'


class ModerationAction(InternalAPIMixin, db.Model):
    __tablename__ = 'moderation_actions'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action_type = db.Column(db.Enum(ActionType), nullable=False)
    moderator_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=timezone.now)
    finish_at = db.Column(db.DateTime)
    reason = db.Column(db.String(512), nullable=False)
    extra_data = db.Column(JSONType, nullable=False, default={})

    async def get_user(self) -> RemoteUser:
        return await self.internal_request(
            'login', 'get_user', user_id=self.user_id, include_profile=False)

    async def get_moderator(self) -> RemoteUser:
        return await self.internal_request(
            'login', 'get_user', user_id=self.moderator_id, include_profile=False)

    def turn_on(self, commit: bool = False) -> None:
        self.is_active = True
        self.save(commit)

    def turn_off(self, commit: bool = False) -> None:
        self.is_active = False
        self.save(commit)

    def time_limited(self) -> bool:
        return self.finish_at is not None

    def finish_in(self) -> Optional[timedelta]:
        if self.time_limited():
            return self.finish_at - timezone.now()

    def finished(self) -> Optional[bool]:
        if self.time_limited():
            return self.finish_at > timezone.now()

    def active(self) -> bool:
        finished = self.finished()
        if finished is None:
            return self.is_active
        return self.is_active and not finished

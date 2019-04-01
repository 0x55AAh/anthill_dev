# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.framework.utils.translation import translate as _
from anthill.platform.api.internal import InternalAPIMixin
from sqlalchemy_utils.types import ChoiceType


class AuditLog(InternalAPIMixin, db.Model):
    __tablename__ = 'audit_log'

    ACTIONS = (
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=timezone.now)
    service_name = db.Column(db.String(512), nullable=False)
    model_name = db.Column(db.String(512), nullable=False)
    object_id = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, nullable=False)
    action = db.Column(ChoiceType(ACTIONS), nullable=False)
    current_version = db.Column(db.Integer, nullable=False)
    previous_version = db.Column(db.Integer, nullable=False)

    async def get_author(self):
        return await self.internal_request('login', 'get_user', user_id=self.author_id)

    async def _get_version_object(self, version):
        kwargs = {
            'model_name': self.model_name,
            'object_id': self.object_id,
            'version': version
        }
        return self.internal_request(service_name, 'object_version', **kwargs)

    async def get_current_object(self):
        return await self._get_version_object(version=self.current_version)

    async def get_previous_object(self):
        return await self._get_version_object(version=self.previous_version)

    async def recover(self):
        kwargs = {
            'model_name': self.model_name,
            'object_id': self.object_id,
            'version': self.previous_version
        }
        await self.internal_request(service_name, 'object_recover', **kwargs)


class UpdateLog(InternalAPIMixin, db.Model):
    __tablename__ = 'update_log'

    STATUS = (
        ('success', _('Success')),
        ('error', _('Error')),
        ('running', _('Running')),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    started = db.Column(db.DateTime, default=timezone.now)
    finished = db.Column(db.DateTime)
    item_name = db.Column(db.String(128), nullable=False)
    author_id = db.Column(db.Integer, nullable=False)
    current_version = db.Column(db.Integer, nullable=False)
    previous_version = db.Column(db.Integer, nullable=False)
    last_failure_tb = db.Column(db.Text)

    async def get_author(self):
        return await self.internal_request('login', 'get_user', user_id=self.author_id)

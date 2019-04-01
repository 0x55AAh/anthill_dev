# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.platform.api.internal import InternalAPIMixin
from sqlalchemy_utils.types import ColorType


class Backup(db.Model):
    __tablename__ = 'backups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=timezone.now)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    recoveries = db.relationship('Recovery', backref='backup', lazy='dynamic')
    # TODO: file


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    backups = db.relationship('Backup', backref='group', lazy='dynamic')
    recoveries = db.relationship('Recovery', backref='group', lazy='dynamic')  # TODO: ?
    color = db.Column(ColorType)


class Recovery(InternalAPIMixin, db.Model):
    __tablename__ = 'recoveries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=timezone.now)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))  # TODO: ?
    backup_id = db.Column(db.Integer, db.ForeignKey('backups.id'))
    author_id = db.Column(db.Integer, nullable=False)
    # TODO:

    async def get_author(self):
        return await self.internal_request('login', 'get_user', user_id=self.author_id)


# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.platform.models import BaseApplication, BaseApplicationVersion
from sqlalchemy_utils.types import URLType, JSONType


class Application(BaseApplication):
    __tablename__ = 'applications'


class ApplicationVersion(BaseApplicationVersion):
    __tablename__ = 'application_versions'

    environment_id = db.Column(db.Integer, db.ForeignKey('environments.id'), nullable=False)


class Environment(db.Model):
    __tablename__ = 'environments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(512), nullable=False)
    discovery = db.Column(URLType, nullable=False)
    payload = db.Column(JSONType, nullable=False, default={})
    active = db.Column(db.Boolean, nullable=False, default=True)
    app_versions = db.relationship('ApplicationVersion', backref='environment', lazy='dynamic')

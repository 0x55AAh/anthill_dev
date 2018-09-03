# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.core.files.storage import default_storage
from sqlalchemy_jsonfield import JSONField
from sqlalchemy.schema import UniqueConstraint
from dlc.deploy import Deployment
import enum
import hashlib
import binascii
import ctypes
import pyhash


class Hasher:
    """Hashing class."""
    def __init__(self, data=None):
        self.data = data or b''

    def set(self, data):
        self.data = data or b''

    def update(self, chunk):
        """Updates data with data chunks."""
        self.data += chunk

    # Hashing algorithms supported.

    def sha256(self):
        return hashlib.sha256(self.data).hexdigest()

    def crc32(self):
        v = binascii.crc32(self.data)
        return int(ctypes.c_uint(v).value)

    def super_fast_hash(self):
        return pyhash.super_fast_hash()(self.data)


class DeploymentMethod(db.Model):
    __tablename__ = 'deployment_methods'
    __table_args__ = ()

    # noinspection PyArgumentList
    Names = enum.Enum('Names', list(Deployment().methods_dict))

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Enum(Names), nullable=False)
    data = db.Column(
        JSONField(
            enforce_string=True,
            enforce_unicode=False
        ),
        nullable=False
    )
    applications = db.relationship(
        'Application', backref=db.backref('deployment_method'), lazy='dynamic',
        cascade='all, delete-orphan')

    def get_method(self):
        cls = Deployment().get_method(self.name)
        return cls(**self.data)


class Application(db.Model):
    __tablename__ = 'applications'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    deployment_method_id = db.Column(
        db.Integer, db.ForeignKey('deployment_methods.id'), nullable=False, index=True)
    filters_scheme = db.Column(
        JSONField(
            enforce_string=True,
            enforce_unicode=False
        ),
        nullable=False
    )
    payload_scheme = db.Column(
        JSONField(
            enforce_string=True,
            enforce_unicode=False
        ),
        nullable=False
    )
    versions = db.relationship(
        'ApplicationVersion', backref=db.backref('application'), lazy='dynamic',
        cascade='all, delete-orphan')


class ApplicationVersion(db.Model):
    __tablename__ = 'application_versions'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.String(128), nullable=False)
    application_id = db.Column(
        db.Integer, db.ForeignKey('applications.id'), nullable=False, index=True)
    groups = db.relationship(
        'BundlesGroup', backref=db.backref('application_version'), lazy='dynamic',
        cascade='all, delete-orphan')


class BundlesGroup(db.Model):
    __tablename__ = 'bundle_groups'
    __table_args__ = ()

    @enum.unique
    class Statuses(enum.Enum):
        CREATED = 0
        PUBLISHING = 1
        PUBLISHED = 2
        ERROR = 3

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Enum(Statuses), nullable=False, default=Statuses.CREATED)
    hash_types = db.Column(
        JSONField(
            enforce_string=True,
            enforce_unicode=False
        ),
        nullable=False
    )
    bundles = db.relationship(
        'Bundle', backref=db.backref('group'), lazy='dynamic',
        cascade='all, delete-orphan')
    version_id = db.Column(
        db.Integer, db.ForeignKey('application_versions.id'), nullable=False, index=True)


class Bundle(db.Model):
    __tablename__ = 'bundles'
    __table_args__ = ()

    @enum.unique
    class Statuses(enum.Enum):
        CREATED = 0
        UPLOADED = 1
        DELIVERING = 2
        DELIVERED = 3
        ERROR = 4

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    key = db.Column(db.String(64), nullable=False)
    filename = db.Column(db.String(128), nullable=False, unique=True)
    hash = db.Column(
        JSONField(
            enforce_string=True,
            enforce_unicode=False
        ),
        nullable=False
    )
    filter = db.Column(
        JSONField(
            enforce_string=True,
            enforce_unicode=False
        ),
        nullable=False
    )
    status = db.Column(db.Enum(Statuses), nullable=False, default=Statuses.CREATED)
    group_id = db.Column(
        db.Integer, db.ForeignKey('bundle_groups.id'), nullable=False, index=True)

    @property
    def application_version(self):
        return self.group.application_version

    @property
    def application(self):
        return self.application_version.application

    @property
    def deployment_method(self):
        return self.application.deployment_method

    @property
    def size(self):
        return default_storage.size(self.filename)

    @property
    def url(self):
        deployment_method = self.deployment_method.get_method()
        return deployment_method.url(self.filename)

    def make_hash(self, filename=None, group=None):
        newhash = {}
        group = group or self.group
        filename = filename or self.filename
        with default_storage.open(filename) as fd:
            hasher = Hasher(fd.read())
            for hash_type, hash_is_active in group.hash_types.items():
                if not hash_is_active:
                    # hash type not active, so skip
                    continue
                hash_type = hash_type.lower()
                hashing_method = getattr(hasher, hash_type, None)
                if callable(hashing_method):
                    newhash[hash_type] = hashing_method()
        return newhash

    def update_hash(self):
        self.hash = self.make_hash()


@db.event.listens_for(Bundle, 'before_insert')
def init_hash_on_bundle_create(mapper, connection, target):
    target.update_hash()


@db.event.listens_for(Bundle.filename, 'set')
def update_hash_on_bundle_change(target, value, oldvalue, initiator):
    if value != oldvalue:
        target.update_hash()


@db.event.listens_for(BundlesGroup.hash_types, 'set')
def update_hash_on_group_change(target, value, oldvalue, initiator):
    if value != oldvalue:
        bundles = target.bundles
        for bundle in bundles:
            bundle.refresh_hash()
        db.session.bulk_save_objects(bundles)

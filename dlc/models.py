# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from sqlalchemy_jsonfield import JSONField
from anthill.framework.core.files.storage import default_storage
from anthill.framework.utils.text import class_name
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


class BundlesGroup(db.Model):
    __tablename__ = 'bundle_groups'

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
    bundles = db.relationship('Bundle', backref='group')


class Bundle(db.Model):
    __tablename__ = 'bundles'

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
    def size(self):
        return default_storage.size(self.filename)

    @property
    def url(self):
        return default_storage.url(self.filename)

    def refresh_hash(self):
        newhash = {}
        with default_storage.open(self.filename) as fd:
            hasher = Hasher(fd.read())
            for hash_type, hash_is_active in self.group.hash_types.items():
                if not hash_is_active:
                    # hash type not active, so skip
                    continue
                hash_type = hash_type.lower()
                hashing_method = getattr(hasher, hash_type, None)
                if callable(hashing_method):
                    newhash[hash_type] = hashing_method()
        self.hash = newhash


@db.event.listens_for(Bundle.filename, 'set')
@db.event.listens_for(BundlesGroup.hash_types, 'set')
def refresh_hash(target, value, oldvalue, initiator):
    if value == oldvalue:
        # value not changed, so return
        return
    if isinstance(target, Bundle):
        target.refresh_hash()
    elif isinstance(target, BundlesGroup):
        for bundle in target.bundles:
            bundle.refresh_hash()
    else:
        raise ValueError(
            'Invalid target class: %s' % class_name(target.__class__, path=False))
    db.session.commit()

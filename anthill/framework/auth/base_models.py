from anthill.framework.auth.hashers import make_password, check_password
from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.framework.utils.crypto import salted_hmac
from anthill.framework.auth import password_validation
from anthill.framework.core.mail import send_mail
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy


def is_sequence(arg):
    if hasattr(arg, "strip"):
        return False
    return hasattr(arg, "__getitem__") or hasattr(arg, "__iter__")


def _role_find_or_create(name):
    role = Role.query.filter_by(name=name).first()
    if not role:
        role = Role(name=name)
        db.session.add(role)
    return role


def make_user_role_table(table_name='users', id_column_name='id'):
    """
    Create the user-role association table so that
    it correctly references your own UserMixin subclass.
    """
    return db.Table(
        'user_role',
        db.Column('user_id', db.Integer, db.ForeignKey('{}.{}'.format(table_name, id_column_name))),
        db.Column('role_id', db.Integer, db.ForeignKey('roles.id')), extend_existing=True)


role_ability_table = db.Table(
    'role_ability',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
    db.Column('ability_id', db.Integer, db.ForeignKey('abilities.id')))


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    abilities = db.relationship('Ability', secondary=role_ability_table, backref='roles')

    def __init__(self, name):
        self.name = name.lower()

    def add_abilities(self, *abilities):
        for ability in abilities:
            existing_ability = Ability.query.filter_by(name=ability).first()
            if not existing_ability:
                existing_ability = Ability(ability)
                db.session.add(existing_ability)
                db.session.commit()
            self.abilities.append(existing_ability)

    def remove_abilities(self, *abilities):
        for ability in abilities:
            existing_ability = Ability.query.filter_by(name=ability).first()
            if existing_ability and existing_ability in self.abilities:
                self.abilities.remove(existing_ability)

    def __repr__(self):
        return '<Role(name=%r)>' % self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other or self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)


class Ability(db.Model):
    __tablename__ = 'abilities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name.lower()

    def __repr__(self):
        return '<Ability(name=%r)>' % self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other or self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)


class UserMixin(db.Model):
    __abstract__ = True

    def __init__(self, roles=None, default_role='user', **kwargs):
        super().__init__(**kwargs)
        # If only a string is passed for roles, convert it to a list containing
        # that string
        if roles and isinstance(roles, str):
            roles = [roles]

        # If a sequence is passed for roles (or if roles has been converted to
        # a sequence), fetch the corresponding database objects and make a list
        # of those.
        if roles and is_sequence(roles):
            self.roles = roles
        # Otherwise, assign the default 'user' role. Create that role if it
        # doesn't exist.
        elif default_role:
            self.roles = [default_role]

    @hybrid_property
    def _id_column_name(self):
        # the list of the class's columns (with attributes like
        # 'primary_key', etc.) is accessible in different places
        # before and after table definition.
        if self.__tablename__ in self.metadata.tables.keys():
            # after definition, it's here
            columns = self.metadata.tables[self.__tablename__]._columns
        else:
            # before, it's here
            columns = self.__dict__

        for k, v in columns.items():
            if getattr(v, 'primary_key', False):
                return k

    @declared_attr
    def _roles(self):
        user_role_table = make_user_role_table(self.__tablename__, self._id_column_name.fget(self))
        return db.relationship('Role', secondary=user_role_table, backref='users')

    @declared_attr
    def roles(self):
        return association_proxy('_roles', 'name', creator=_role_find_or_create)

    def add_roles(self, *roles):
        self.roles.extend([role for role in roles if role not in self.roles])

    def remove_roles(self, *roles):
        self.roles = [role for role in self.roles if role not in roles]

    @property
    def abilities(self):
        return Ability.query.filter(Ability.roles.in_(self._roles))


class BaseAbstractUser(UserMixin, db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, nullable=False, default=timezone.now)
    last_login = db.Column(db.DateTime, nullable=True, default=None)
    password = db.Column(db.String)

    # Stores the raw password if set_password() is called so that it can
    # be passed to password_changed() after the model is saved.
    _password = None

    def get_username(self):
        """Return the identifying username for this User."""
        return getattr(self, self.USERNAME_FIELD)

    def __str__(self):
        return self.get_username()

    def __repr__(self):
        return '<User(name=%r)>' % self.get_username()

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct.
        Handles hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save()
        return check_password(raw_password, self.password, setter=setter)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None
        return self

    def get_session_auth_hash(self):
        """Return an HMAC of the password field."""
        key_salt = "anthill.framework.auth.models.BaseAbstractUser.get_session_auth_hash"
        return salted_hmac(key_salt, self.password).hexdigest()


class AbstractUser(BaseAbstractUser):
    __abstract__ = True

    username = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    USERNAME_FIELD = 'username'

    @classmethod
    def __declare_last__(cls):
        """Validation must be here."""

    @property
    def is_authenticated(self):
        return True

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

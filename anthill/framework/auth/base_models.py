from anthill.framework.auth.hashers import make_password, check_password
from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.framework.utils.crypto import salted_hmac
from anthill.framework.auth import password_validation
from anthill.framework.core.mail import send_mail
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr


class AbilitiesMixin:
    abilities_text = db.Column(db.Text())

    def __init__(self):
        super(AbilitiesMixin, self).__init__()
        self.abilities_text = ""
        self.abilities = None

    @property
    def abilities(self):
        return set(filter(None, self.abilities_text.split("\n")))

    @abilities.setter
    def abilities(self, new_abilities):
        self.abilities_text = "\n".join(set(new_abilities))

    # noinspection PyMethodMayBeStatic
    def _check_abilities(self, abilities):
        if not isinstance(abilities, (list, tuple)):
            raise ValueError('Abilities has to be list or tuple')

    def add_abilities(self, new_abilities):
        self._check_abilities(new_abilities)
        self.abilities = self.abilities.union(new_abilities)

    def remove_abilities(self, old_abilities):
        self._check_abilities(old_abilities)
        self.abilities = self.abilities.difference(old_abilities)

    def has_ability(self, ability):
        if ability in self.abilities:
            return True

        while "." in ability:
            ability, ability_suffix = ability.rsplit(".", 1)
            if ability in self.abilities:
                return True

        return False


class RoleMixin(AbilitiesMixin):
    """Subclass this for your role model."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, name=None):
        super(RoleMixin, self).__init__()
        if name:
            self.name = name.lower()

    def __str__(self):
        return self.name


class UserMixin(AbilitiesMixin):
    """Subclass this for your user model."""

    def __init__(self, roles=None):
        super(UserMixin, self).__init__()
        # If only a string is passed for roles, convert it to a list containing
        # that string
        if roles and isinstance(roles, RoleMixin):
            self.roles = [roles]
            return

        # If a sequence is passed for roles (or if roles has been converted to
        # a sequence), fetch the corresponding database objects and make a list
        # of those.
        if roles and all(isinstance(role, RoleMixin) for role in roles):
            self.roles = roles
            return

        if roles:
            raise ValueError("Invalid roles")

    # noinspection PyUnresolvedReferences
    @declared_attr
    def roles(self):
        users_roles_table = db.Table(
            "%s_%s" % (self.__tablename__, self.__roleclass__.__tablename__),
            self.metadata,
            db.Column("id", db.Integer, primary_key=True),
            db.Column("user_id", db.Integer, db.ForeignKey("%s.id" % self.__tablename__), nullable=False),
            db.Column("role_id", db.Integer, db.ForeignKey("%s.id" % self.__roleclass__.__tablename__), nullable=False),
            db.UniqueConstraint("user_id", "role_id"),
        )
        return relationship("Role", secondary=users_roles_table, backref="users")

    def add_roles(self, roles):
        if not isinstance(roles, (list, tuple)):
            raise ValueError("Invalid roles")

        for role in roles:
            if isinstance(role, RoleMixin):
                if role not in self.roles:
                    self.roles.append(role)
                # TODO: Option to add role by role name

        self.roles.extend([role for role in roles if role not in self.roles])

    def remove_roles(self, roles):
        if not isinstance(roles, (list, tuple)):
            raise ValueError("Invalid roles")

        self.roles = [role for role in self.roles if role not in roles]

    def has_role(self, role):
        if isinstance(role, RoleMixin):
            return role in self.roles
        elif isinstance(role, str):
            return True if next((role_ for role_ in self.roles if role_.name == role), None) else False

    @AbilitiesMixin.abilities.getter
    def abilities(self):
        user_abilities = super(UserMixin, self).abilities

        for role in self.roles:
            user_abilities.update(role.abilities)

        return user_abilities


class Role(RoleMixin, db.Model):
    __tablename__ = 'roles'


class BaseAbstractUser(UserMixin, db.Model):
    __roleclass__ = Role
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

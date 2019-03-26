# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.framework.utils.module_loading import import_string
from anthill.framework.utils.functional import cached_property


bot_action_association = db.Table(
    'bot_action_association', db.metadata,
    db.Column('bot_id', db.ForeignKey('bots.id'), primary_key=True),
    db.Column('action_id', db.ForeignKey('actions.id'), primary_key=True)
)


class Bot(db.Model):
    __tablename__ = 'bots'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.String(512), nullable=False)
    created = db.Column(db.DateTime, default=timezone.now)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    actions = db.relationship('Action', secondary=bot_action_association, backref='bots', lazy='dynamic')

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Bot(name=%s, description=%s)>" % (self.name, self.description)


class Action(db.Model):
    __tablename__ = 'actions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(512), nullable=False)
    value = db.Column(db.String(512), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return "<Action(name=%s, description=%s, value=%s)>" % (self.name, self.description, self.value)

    @cached_property
    def value_object(self):
        return import_string(self.value)()

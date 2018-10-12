# For more details, see
# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
from anthill.framework.db import db


class Event(db.Model):
    __tablename__ = 'events'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


class EventCategory(db.Model):
    __tablename__ = 'event_categories'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


class EventGenerator(db.Model):
    __tablename__ = 'event_generators'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


class EventGeneratorPool(db.Model):
    __tablename__ = 'event_generator_pools'
    __table_args__ = ()

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

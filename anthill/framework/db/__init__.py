from anthill.framework.apps.builder import app
from .marshmallow import Marshmallow
from .sqlalchemy import SQLAlchemy
from .management import Migrate


__all__ = ['db', 'ma']


db = SQLAlchemy(app)
migrate = Migrate(app, db)


def save(instance, **kwargs):
    db.session.add(instance)
    db.session.commit()


def delete(instance, **kwargs):
    db.session.delete(instance)
    db.session.commit()


setattr(db.Model, 'save', save)
setattr(db.Model, 'delete', delete)


ma = Marshmallow(app)

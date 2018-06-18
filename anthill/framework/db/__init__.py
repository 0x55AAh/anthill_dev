from anthill.framework.apps.builder import app
from .marshmallow import Marshmallow
from .sqlalchemy import SQLAlchemy
from .management import Migrate


__all__ = ['db', 'ma']


db = SQLAlchemy(app)
migrate = Migrate(app, db)


def _save(instance, **kwargs):
    db.session.add(instance)
    db.session.commit()


def _delete(instance, **kwargs):
    db.session.delete(instance)
    db.session.commit()


setattr(db.Model, 'save', _save)
setattr(db.Model, 'delete', _delete)

del _save
del _delete


ma = Marshmallow(app)

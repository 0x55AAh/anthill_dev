from anthill.framework.apps.builder import app
from anthill.framework.db.marshmallow import Marshmallow
from anthill.framework.db.sqlalchemy import SQLAlchemy
from anthill.framework.db.management import Migrate


__all__ = ['db', 'ma']


db = SQLAlchemy(app)
migrate = Migrate(app, db)


def _save(instance, force_insert=False):
    if force_insert:
        db.session.add(instance)
    db.session.commit()


def _delete(instance):
    db.session.delete(instance)
    db.session.commit()


setattr(db.Model, 'save', _save)
setattr(db.Model, 'delete', _delete)

del _save
del _delete


ma = Marshmallow(app)

from sqlalchemy.ext.declarative import declarative_base
from anthill.framework.apps.builder import app
from anthill.framework.core.exceptions import ImproperlyConfigured
from anthill.framework.db.marshmallow import Marshmallow
from anthill.framework.db.sqlalchemy import SQLAlchemy, DefaultMeta, Model as DefaultModel
from anthill.framework.db.sqlalchemy.activerecord import ActiveRecord
from anthill.framework.db.management import Migrate


__all__ = ['db', 'ma']


class Model(ActiveRecord):
    # def save(self, force_insert=False):
    #     if force_insert:
    #         self.session.add(self)
    #     self.session.flush()
    #     return self

    def dump(self):
        """Marshmallow default schema data dump."""
        try:
            schema_class = getattr(self, '__marshmallow__')
        except AttributeError:
            raise ImproperlyConfigured('Schema class is undefined')
        return schema_class().dump(self)


Base = declarative_base(cls=Model, metaclass=DefaultMeta, name='Model')


db = SQLAlchemy(app, model_class=Base)
migrate = Migrate(app, db)
ma = Marshmallow(app)

from sqlalchemy.ext.declarative import declarative_base
from anthill.framework.apps.builder import app
from anthill.framework.core.exceptions import ImproperlyConfigured
from anthill.framework.db.marshmallow import Marshmallow
from anthill.framework.db.sqlalchemy import SQLAlchemy, DefaultMeta, Model as DefaultModel
from anthill.framework.db.management import Migrate


__all__ = ['db', 'ma']


class Model(DefaultModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = None

    @property
    def db(self):
        return db

    @property
    def session(self):
        return db.session

    def save(self, force_insert=False):
        if force_insert:
            self.session.add(self)
        self.session.commit()

    def delete(self):
        self.session.delete(self)
        self.session.commit()

    def dump(self):
        """Marshmallow data dump."""
        if not getattr(self, 'schema', None):
            try:
                schema_class = getattr(self, 'Schema')
            except AttributeError:
                raise ImproperlyConfigured('Schema class is undefined')
            self.schema = schema_class()
        return self.schema.dump(self)


db = SQLAlchemy(
    app,
    model_class=declarative_base(
        cls=Model, metaclass=DefaultMeta, name='Model')
)
migrate = Migrate(app, db)
ma = Marshmallow(app)

from sqlalchemy.ext.declarative import declarative_base
from anthill.framework.apps.builder import app
from anthill.framework.core.exceptions import ImproperlyConfigured
from anthill.framework.db.marshmallow import Marshmallow
from anthill.framework.db.sqlalchemy import (
    SQLAlchemy, DefaultMeta, Model as DefaultModel, BaseQuery)
from anthill.framework.db.sqlalchemy.activerecord import ActiveRecordMixin
from anthill.framework.db.management import Migrate
from anthill.framework.utils.translation import translate_lazy as _

__all__ = ['db', 'ma']


class Model(ActiveRecordMixin, DefaultModel):
    __default_abilities__ = (
        ('can_create', _('Can create model')),
        ('can_update', _('Can update model')),
        ('can_delete', _('Can delete model')),
        ('can_view', _('Can view model')),
    )
    __abilities__ = ()

    # def save(self, force_insert=False):
    #     if force_insert:
    #         self.session.add(self)
    #     self.session.flush()
    #     return self

    @classmethod
    def get_abilities(cls):
        return cls.__default_abilities__ + cls.__abilities__

    def dump(self):
        """Marshmallow default schema data dump."""
        try:
            schema_class = getattr(self, '__marshmallow__')
        except AttributeError:
            raise ImproperlyConfigured('Schema class is undefined')
        return schema_class().dump(self)


Base = declarative_base(cls=Model, metaclass=DefaultMeta, name='Model')

db = SQLAlchemy(app, query_class=BaseQuery, model_class=Base)
migrate = Migrate(app, db)
ma = Marshmallow(app)

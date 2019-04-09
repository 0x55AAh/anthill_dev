from anthill.framework.core.exceptions import ImproperlyConfigured
from anthill.platform.api.internal import connector


class RemoteModelMixin:
    """Mixin class for representing model object from remote server."""

    IDENTIFIER_FIELD = 'id'
    model_name = None  # Format: `<service_name>.<model_name>`

    def _parse_model_name(self):
        return self.model_name.split('.')

    def get_service_name(self):
        return self._parse_model_name()[0]

    def get_model_name(self):
        return self._parse_model_name()[1]

    def get_identifier(self):
        """Return the identifying field for this RemoteModelMixin."""
        return getattr(self, self.IDENTIFIER_FIELD)

    async def request(self, action, **kwargs):
        return await connector.internal_request(self.get_service_name(), action, **kwargs)

    async def model_fields(self):
        """Inspect model for field names."""
        return await self.request('model_fields', model_name=self.get_model_name())

    def _set_data(self, **kwargs):
        self.__dict__.update(kwargs)

    async def get_data(self):
        model_fields = await self.get_model_fields()
        return dict((f, getattr(self, f)) for f in model_fields)

    async def sync(self):
        return await self.get()

    async def get(self):
        """Perform get model operation on remote server."""
        kwargs = await self.request(
            'get_model',
            model_name=self.get_model_name(),
            object_id=self.get_identifier()
        )
        self._set_data(**kwargs)
        return self

    async def create(self):
        """Perform create model operation on remote server."""
        await self.request(
            'create_model',
            model_name=self.get_model_name(),
            **(await self.get_data())
        )
        return self

    async def update(self):
        """Perform update model operation on remote server."""
        await self.request(
            'update_model',
            model_name=self.get_model_name(),
            object_id=self.get_identifier(),
            **(await self.get_data())
        )
        return self

    async def delete(self):
        """Perform delete model operation on remote server."""
        await self.request(
            'delete_model',
            model_name=self.get_model_name(),
            object_id=self.get_identifier()
        )

    async def get_model_fields(self):
        if not getattr(self, '_model_fields', None):
            model_fields = await self.model_fields()
            setattr(self, '_model_fields', model_fields)
        return self._model_fields

    async def save(self, force_insert=False):
        if force_insert:
            return await self.create()
        return await self.update()


class RemoteModel(RemoteModelMixin):
    """Class for representing model object from remote server."""

    def __init__(self, **kwargs):
        self._set_data(**kwargs)

    def __repr__(self):
        return '<RemoteModel(service=%(service)s, model=%(model)s, identifier=%(identifier)s)>' % {
            'service': self.get_service_name(),
            'model': self.get_model_name(),
            'identifier': self.get_identifier()
        }

    def __str__(self):
        return str(self.get_identifier())

    # def get_absolute_url(self):
    #    pass


class RemoteModelBuilder:
    @classmethod
    def get_model_name(cls, full_model_name):
        return full_model_name.split('.')[-1]

    @classmethod
    def build(cls, full_model_name):
        model_name = cls.get_model_name(full_model_name)
        return type(model_name, (RemoteModel,), {'model_name': full_model_name})

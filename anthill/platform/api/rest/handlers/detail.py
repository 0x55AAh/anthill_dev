from .base import APIHandler
from anthill.framework.handlers.detail import SingleObjectMixin


class DetailHandler(SingleObjectMixin, APIHandler):
    """A base handler for displaying a single object in JSON format."""
    # Marshmellow schema class
    schema_class = None

    def dump_object(self):
        if self.schema_class:
            schema = self.schema_class()
            return schema.dump(self.object)
        else:
            return self.object.dump()

    async def get(self, *args, **kwargs):
        # noinspection PyAttributeOutsideInit
        self.object = await self.get_object()
        object_dump = self.dump_object().data
        self.write({'data': object_dump})

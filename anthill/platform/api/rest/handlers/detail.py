from anthill.framework.handlers.base import JSONHandler
from anthill.framework.handlers.detail import SingleObjectMixin


class DetailHandler(SingleObjectMixin, JSONHandler):
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
        data = {}
        try:
            # noinspection PyAttributeOutsideInit
            self.object = await self.get_object()
            object_dump = self.dump_object().data
            data.update(data=object_dump)
        except Exception as e:
            data.update(errors=[str(e)])
        self.write(data)

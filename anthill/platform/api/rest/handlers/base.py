from anthill.framework.handlers import RequestHandler, JSONHandlerMixin


class MarshmallowMixin:
    schema_class = None

    def get_schema_class(self):
        return self.schema_class

    def get_schema(self):
        schema_class = self.get_schema_class()
        return schema_class()

    def serialize_data(self, data):
        pass


class APIHandlerMixin(MarshmallowMixin, JSONHandlerMixin):
    pass


class APIHandler(APIHandlerMixin, RequestHandler):
    pass


from anthill.framework.utils.module_loading import import_string


class BaseLoader:
    _model = None

    def __init__(self):
        if self._model is not None:
            self.model = import_string(self._model)
        else:
            self.model = None

    async def size(self):
        raise NotImplementedError

    async def filter_objects(self, *criteria, **filters):
        raise NotImplementedError

    async def get_objects(self):
        raise NotImplementedError

    async def get_object(self, id_):
        raise NotImplementedError

    async def remove_object(self, id_):
        raise NotImplementedError

    async def create_object(self, **kwargs):
        raise NotImplementedError

    async def update_object(self, **kwargs):
        raise NotImplementedError

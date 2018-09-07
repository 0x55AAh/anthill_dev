from anthill.framework.utils.asynchronous import as_future
from anthill.platform.atomic.loaders.base import BaseLoader
import logging

logger = logging.getLogger('anthill.application')


class Loader(BaseLoader):
    _model = 'anthill.platform.atomic.models.Transaction'

    @as_future
    def filter_objects(self, *criteria, **filters):
        return self.model.find_by(*criteria, **filters)

    @as_future
    def get_objects(self):
        return self.model.all()

    @as_future
    def get_object(self, id_):
        return self.model.find(id_)

    @as_future
    def remove_object(self, id_):
        self.model.destroy([id_])

    @as_future
    def create_object(self, **kwargs):
        return self.model.create(**kwargs)

    @as_future
    def update_object(self, **kwargs):
        return self.model.update(**kwargs)

    @as_future
    def size(self):
        self.model.count()

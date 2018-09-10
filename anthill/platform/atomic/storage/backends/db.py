from anthill.framework.utils.asynchronous import as_future
from anthill.platform.atomic.storage.backends.base import BaseStorage
import logging

logger = logging.getLogger('anthill.application')


class Storage(BaseStorage):
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
    def update_object_by_id(self, id_, **kwargs):
        return self.model.find(id_).update(**kwargs)

    @as_future
    def update_object(self, obj, **kwargs):
        return obj.update(**kwargs)

    @as_future
    def size(self):
        return self.model.count()

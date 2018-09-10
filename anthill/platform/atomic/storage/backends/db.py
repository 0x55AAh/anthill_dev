from anthill.framework.utils.asynchronous import as_future
from anthill.platform.atomic.storage.backends.base import BaseStorage
from typing import List, TypeVar
import logging

Transaction = TypeVar('Transaction')

logger = logging.getLogger('anthill.application')


class Storage(BaseStorage):
    _model = 'anthill.platform.atomic.models.Transaction'

    @as_future
    def filter_objects(self, *criteria, **filters) -> List[Transaction]:
        return self.model.find_by(*criteria, **filters)

    @as_future
    def get_objects(self) -> List[Transaction]:
        return self.model.all()

    @as_future
    def get_object(self, id_: int) -> Transaction:
        return self.model.find(id_)

    @as_future
    def remove_object(self, id_: int) -> None:
        self.model.destroy([id_])

    @as_future
    def create_object(self, **kwargs) -> Transaction:
        return self.model.create(**kwargs)

    @as_future
    def update_object_by_id(self, id_: int, **kwargs) -> Transaction:
        return self.model.find(id_).update(**kwargs)

    @as_future
    def update_object(self, obj: Transaction, **kwargs) -> Transaction:
        return obj.update(**kwargs)

    @as_future
    def size(self) -> int:
        return self.model.count()

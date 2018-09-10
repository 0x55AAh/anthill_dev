from anthill.framework.utils.module_loading import import_string
from anthill.framework.core.exceptions import ImproperlyConfigured
from typing import List, TypeVar

Transaction = TypeVar('Transaction')


class BaseStorage:
    _model: str = None

    def __init__(self):
        if self._model is None:
            raise ImproperlyConfigured('Model not defined')
        self.model = import_string(self._model)

    async def size(self) -> int:
        raise NotImplementedError

    async def filter_objects(self, *criteria, **filters) -> List[Transaction]:
        raise NotImplementedError

    async def get_objects(self) -> List[Transaction]:
        raise NotImplementedError

    async def get_object(self, id_: int) -> Transaction:
        raise NotImplementedError

    async def remove_object(self, id_: int) -> None:
        raise NotImplementedError

    async def create_object(self, **kwargs) -> Transaction:
        raise NotImplementedError

    async def update_object(self, obj: Transaction, **kwargs) -> Transaction:
        raise NotImplementedError

    async def update_object_by_id(self, id_: int, **kwargs) -> Transaction:
        raise NotImplementedError

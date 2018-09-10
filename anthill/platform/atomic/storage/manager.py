from anthill.framework.utils.module_loading import import_string
from anthill.framework.conf import settings
from typing import List, TypeVar
import logging

logger = logging.getLogger('anthill.application')


TRANSACTION_SETTINGS = getattr(settings, 'TRANSACTION', {})
STORAGE = TRANSACTION_SETTINGS.get('STORAGE', {})
STORAGE_BACKEND = STORAGE.get('BACKEND', 'anthill.platform.atomic.storage.backends.db.Storage')

Transaction = TypeVar('Transaction')


class DataManager:
    _storage_class: str = STORAGE_BACKEND

    def __init__(self):
        self.storage = import_string(self._storage_class)()

    async def size(self) -> int:
        return await self.storage.size()

    async def create_transaction(self, **kwargs) -> Transaction:
        transaction = await self.storage.create_object(**kwargs)
        logger.info('Transaction created: %s' % transaction.id)
        return transaction

    async def delete_transaction(self, id_: int) -> None:
        await self.storage.remove_object(id_)
        logger.info('Transaction deleted: %s' % id_)

    async def update_transaction(self, transaction: Transaction, **kwargs) -> None:
        await self.storage.update_object(transaction, **kwargs)
        logger.info('Transaction updated: %s' % transaction.id)

    async def update_transaction_by_id(self, id_: int, **kwargs) -> Transaction:
        transaction = await self.storage.update_object_by_id(id_, **kwargs)
        logger.info('Transaction updated: %s' % transaction.id)
        return transaction

    async def get_transactions(self) -> List[Transaction]:
        transactions = await self.storage.get_objects()
        return transactions

    async def get_transaction(self, id_: int) -> Transaction:
        transaction = await self.storage.get_object(id_)
        return transaction

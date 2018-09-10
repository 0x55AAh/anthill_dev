from anthill.framework.utils.module_loading import import_string
from anthill.framework.conf import settings
import logging

logger = logging.getLogger('anthill.application')


TRANSACTION_SETTINGS = getattr(settings, 'TRANSACTION', {})
STORAGE = TRANSACTION_SETTINGS.get('STORAGE', {})
STORAGE_BACKEND = STORAGE.get('BACKEND', 'anthill.platform.atomic.storage.backends.db.Storage')


class DataManager:
    _storage_class = STORAGE_BACKEND

    def __init__(self):
        self.storage = import_string(self._storage_class)()

    async def size(self):
        return await self.storage.size()

    async def create_transaction(self, **kwargs):
        transaction = await self.storage.create_object(**kwargs)
        logger.info('Transaction created: %s' % transaction.id)
        return transaction

    async def delete_transaction(self, id_):
        await self.storage.remove_object(id_)
        logger.info('Transaction deleted: %s' % id_)

    async def update_transaction(self, transaction, **kwargs):
        await self.storage.update_object(transaction, **kwargs)
        logger.info('Transaction updated: %s' % transaction.id)

    async def update_transaction_by_id(self, id_, **kwargs):
        transaction = await self.storage.update_object_by_id(id_, **kwargs)
        logger.info('Transaction updated: %s' % transaction.id)
        return transaction

    async def get_transactions(self):
        return await self.storage.get_objects()

    async def get_transaction(self, id_):
        return await self.storage.get_object(id_)

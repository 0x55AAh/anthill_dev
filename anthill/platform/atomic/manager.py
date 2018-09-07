from anthill.framework.utils.singleton import Singleton
from anthill.framework.utils.module_loading import import_string
from anthill.framework.conf import settings
from tornado.ioloop import IOLoop
import logging

logger = logging.getLogger('anthill.application')


MANAGER_SETTINGS = getattr(settings, 'TRANSACTION_MANAGER', {})
LOADER = MANAGER_SETTINGS.get('LOADER', 'anthill.platform.atomic.loaders.db.Loader')


class TransactionManager(Singleton):
    _loader_class = LOADER

    def __init__(self):
        self.loader = import_string(self._loader_class)()
        IOLoop.current().add_callback(self.start)

    async def size(self):
        return await self.loader.size()

    async def create_transaction(self, **kwargs):
        transaction = await self.loader.create_object(**kwargs)
        logger.info('Transaction created: %s' % transaction.id)
        return transaction

    async def delete_transaction(self, id_):
        await self.loader.remove_object(id_)
        logger.info('Transaction deleted: %s' % transaction.id)

    async def get_transactions(self):
        return await self.loader.get_objects()

    async def get_transaction(self, id_):
        return await self.loader.get_object(id_)

    async def start(self):
        logger.info('Transaction manager started.')

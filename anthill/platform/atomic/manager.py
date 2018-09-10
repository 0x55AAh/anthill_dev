from anthill.framework.utils.singleton import Singleton
from anthill.platform.atomic.storage.manager import DataManager
from anthill.framework.conf import settings
from tornado.ioloop import IOLoop
import logging

logger = logging.getLogger('anthill.application')


TRANSACTION_SETTINGS = getattr(settings, 'TRANSACTION', {})
STORAGE = TRANSACTION_SETTINGS.get('STORAGE', {})
STORAGE_BACKEND = STORAGE.get('BACKEND', 'anthill.platform.atomic.storage.backends.db.Storage')


class TransactionManager(Singleton):
    data_manager_class = DataManager

    def __init__(self):
        self.data_manager = self.data_manager_class()
        IOLoop.current().add_callback(self.start)

    async def on_start(self):
        pass

    async def start(self):
        await self.on_start()
        logger.info('Transaction manager started.')

from anthill.framework.utils.singleton import Singleton
from anthill.platform.atomic.storage.manager import DataManager
from anthill.platform.atomic.strategy import rollback
from tornado.ioloop import IOLoop
import logging

logger = logging.getLogger('anthill.application')


class TransactionManager(Singleton):
    data_manager_class = DataManager
    strategy_class = rollback.Strategy

    def __init__(self):
        self.strategy = self.strategy_class()
        self.data_manager = self.data_manager_class()
        IOLoop.current().add_callback(self.start)

    async def on_start(self) -> None:
        pass

    async def start(self) -> None:
        await self.on_start()
        logger.info('Transaction manager started.')

from anthill.framework.utils.singleton import Singleton
from anthill.platform.atomic.storage.manager import DataManager
from anthill.platform.atomic.strategy import rollback
from tornado.ioloop import IOLoop
from sqlalchemy import or_
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
        from anthill.platform.atomic.models import Status
        t_model = self.data_manager.storage.model
        failed_transactions = await self.data_manager.get_transactions(
            or_(t_model.status == Status.FAILED, t_model.status == Status.ROLLBACK_FAILED))
        for transaction in failed_transactions:
            await self.strategy.proceed(transaction)
        logger.info('%s transactions loaded for restore.' % len(failed_transactions))

    async def start(self) -> None:
        await self.on_start()
        logger.info('Transaction manager started.')

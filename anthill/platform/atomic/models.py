from anthill.framework.db import db
from anthill.framework.utils import timezone
from anthill.platform.atomic.manager import TransactionManager
from anthill.platform.atomic.exceptions import TransactionError, TransactionTimeoutError
from tornado.gen import sleep
from tornado.ioloop import IOLoop
import enum
import logging
import inspect

logger = logging.getLogger('anthill.application')


@enum.unique
class Status(enum.Enum):
    NEW = 0
    STARTED = 1
    SUCCESSFUL = 2
    FAILED = 3
    RESUMED = 4
    ROLLBACK_STARTED = 10
    ROLLBACK_SUCCESSFUL = 11
    ROLLBACK_FAILED = 12


class BaseTransaction(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # TODO: UUID type
    started = db.Column(db.DateTime, nullable=False, default=timezone.now)
    finished = db.Column(db.DateTime)
    status = db.Column(db.Enum(Status), nullable=False, default=Status.NEW)
    timeout = db.Column(db.Integer, nullable=False, default=0)
    is_commited = db.Column(db.Boolean, nullable=False, default=False)

    PROCEED_RETRY_TIMEOUT = 1
    PROCEED_RETRY_LIMIT = 3

    @property
    def manager(self):
        return TransactionManager()

    @property
    def strategy(self):
        return self.manager.strategy

    def is_finished(self):
        return self.finished is not None

    def check_timeout(self):
        if not self.is_finished():
            if timezone.now() - self.started > self.timeout:
                raise TransactionTimeoutError('Transaction timeout: %s' % self.timeout)

    def commit_finish(self):
        self.status = Status.SUCCESSFUL
        self.finished = timezone.now()
        self.is_commited = True
        self.save()  # TODO: async

    def rollback_start(self):
        self.status = Status.ROLLBACK_STARTED
        self.save()  # TODO: async

    def rollback_finish(self):
        self.status = Status.ROLLBACK_SUCCESSFUL
        self.finished = timezone.now()
        self.is_commited = True
        self.save()  # TODO: async

    async def commit(self):
        raise NotImplementedError

    async def rollback(self):
        raise NotImplementedError


class Transaction(BaseTransaction):
    __tablename__ = 'transactions'
    __table_args__ = ()

    tasks = db.relationship(
        'TransactionTask', backref=db.backref('transaction'), lazy='dynamic',
        cascade='all, delete-orphan')
    state = db.Column(db.Integer, nullable=False, default=0)

    def get_tasks(self):
        return self.tasks.all()

    def add(self, task):
        self.tasks.append(task)
        logger.info('Transaction task appended: %s' % task.id)

    def create_task(self, *args, **kwargs):
        task = TransactionTask(*args, **kwargs)
        self.tasks.append(task)
        logger.info('Transaction task created: %s' % task.id)
        return task

    def delete_task(self, id_):
        task = self.tasks.get(id_)
        self.tasks.remove(task)
        logger.info('Transaction task deleted: %s' % id_)

    def size(self):
        return self.tasks.count()

    async def commit(self, resume=False):
        self.commit_start(resume)
        tasks = self.get_tasks()
        for task in tasks[self.state:] if resume else tasks:
            rr = range(self.PROCEED_RETRY_LIMIT)
            try:
                for i in rr:
                    try:
                        await task.commit()
                        break
                    except TransactionError:
                        if i == rr[-1]:
                            raise
                        await sleep(self.PROCEED_RETRY_TIMEOUT)
            except TransactionError:
                self.status = Status.FAILED
                self.save()  # TODO: async
                return
            else:
                self.state_incr()
        self.commit_finish()

    async def resume(self):
        await self.commit(resume=True)

    def state_incr(self):
        self.state += 1
        self.save()  # TODO: async

    def state_decr(self):
        self.state -= 1
        self.save()  # TODO: async

    def commit_start(self, resume=False):
        self.status = Status.RESUMED if resume else Status.STARTED
        transaction_watcher = self.strategy.get_task('TRANSACTION')
        transaction_watcher.apply_async((self.id,), countdown=self.timeout)
        self.save()  # TODO: async

    async def rollback(self):
        self.rollback_start()
        for task in self.get_tasks()[:self.state]:
            rr = range(self.PROCEED_RETRY_LIMIT)
            try:
                for i in rr:
                    try:
                        await task.rollback()
                        break
                    except TransactionError:
                        if i == rr[-1]:
                            raise
                        await sleep(self.PROCEED_RETRY_TIMEOUT)
            except TransactionError:
                self.status = Status.ROLLBACK_FAILED
                self.save()  # TODO: async
                return
            else:
                self.state_decr()
        self.rollback_finish()


class TransactionTask(BaseTransaction):
    __tablename__ = 'transaction_tasks'
    __table_args__ = ()

    transaction_id = db.Column(
        db.Integer, db.ForeignKey('transactions.id'), nullable=False, index=True)

    def commit_start(self):
        self.status = Status.STARTED
        transaction_watcher = self.strategy.get_task('TRANSACTION_TASK')
        transaction_watcher.apply_async(
            (self.transaction.id, self.id), countdown=self.timeout)

    async def commit(self):
        self.commit_start()
        try:
            # TODO
            pass
        except Exception as e:
            raise TransactionError from e
        self.commit_finish()

    async def rollback(self):
        self.rollback_start()
        try:
            # TODO
            pass
        except Exception as e:
            raise TransactionError from e
        self.rollback_finish()


class ExecutableWrapper:
    def __init__(self, field, func, *args, **kwargs):
        self.field = field    # model.field
        self.func = func      # function object
        self.args = args
        self.kwargs = kwargs
        self.prepared = False
        IOLoop.current().add_callback(self.prepare)

    async def prepare(self):
        """Save current value of `self.field`."""
        self.prepared = True

    async def upgrade(self):
        """Set new value of `self.field`."""
        if not self.prepared:
            raise ValueError('Not prepared for upgrade.')
        if inspect.iscoroutinefunction(self.func):
            await self.func(*self.args, **self.kwargs)
        else:
            self.func(*self.args, **self.kwargs)

    async def downgrade(self):
        """Restore old value of `self.field`."""
        if self.prepared:
            pass

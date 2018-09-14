from anthill.framework.db import db
from sqlalchemy.types import VARCHAR
from anthill.framework.utils import timezone
from anthill.framework.utils.module_loading import import_string
from anthill.platform.atomic.manager import TransactionManager
from anthill.platform.atomic.exceptions import TransactionError, TransactionTimeoutError
from sqlalchemy_utils.types.uuid import UUIDType
from sqlalchemy_utils.types.json import JSONType
from tornado.gen import sleep
from tornado.ioloop import IOLoop
from functools import partial
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

    id = db.Column(UUIDType(binary=False), primary_key=True)
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

    @property
    def is_finished(self):
        return self.finished is not None

    @property
    def internal_request(self):
        from anthill.platform.utils.internal_api import internal_request
        return internal_request

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

    async def request_transaction(self, service):
        return await self.internal_request(service, 'get_transaction', self.id)

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

    async def commit(self, resume=False, retries=3, retry_timeout=1):
        self.commit_start(resume)
        tasks = self.get_tasks()
        retries = retries or self.PROCEED_RETRY_LIMIT
        retry_timeout = retry_timeout or self.PROCEED_RETRY_TIMEOUT
        for task in tasks[self.state:] if resume else tasks:
            rr = range(retries)
            try:
                for i in rr:
                    try:
                        await task.commit()
                        break
                    except TransactionError:
                        if i == rr[-1]:
                            raise
                        await sleep(retry_timeout)
            except TransactionError:
                self.status = Status.FAILED
                self.save()  # TODO: async
                return
            else:
                self.state_incr()
        self.commit_finish()

    async def resume(self, retries=3, retry_timeout=1):
        await self.commit(
            resume=True, retries=retries, retry_timeout=retry_timeout)

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


class FunctionType(db.TypeDecorator):
    impl = VARCHAR

    # noinspection PyMethodMayBeStatic
    def process_bind_param(self, value, dialect):
        if callable(value):
            return '.'.join([value.__module__, value.__name__])
        return value

    # noinspection PyMethodMayBeStatic
    def process_result_value(self, value, dialect):
        if value is not None:
            return import_string(value)
        return value


class TransactionTask(BaseTransaction):
    __tablename__ = 'transaction_tasks'
    __table_args__ = ()

    @enum.unique
    class Rank(enum.Enum):
        MASTER = 0
        SLAVE = 1

    rank = db.Column(db.Enum(Rank), nullable=False, default=Rank.MASTER)
    master = db.Column(db.String(128))  # Name of master service if rank is SLAVE
    slave = db.Column(db.String(128))   # Name of slave service if rank is MASTER

    func = db.Column(FunctionType, nullable=False)
    func_args = db.Column(JSONType)
    func_kwargs = db.Column(JSONType)

    obj_model_name = db.Column(db.String(512), nullable=False)
    obj_id = db.Column(db.Integer, nullable=False)
    obj_ver = db.Column(db.Integer)

    transaction_id = db.Column(
        UUIDType, db.ForeignKey('transactions.id'), nullable=False, index=True)

    def commit_start(self):
        self.status = Status.STARTED
        transaction_watcher = self.strategy.get_task('TRANSACTION_TASK')
        transaction_watcher.apply_async(
            (self.transaction.id, self.id), countdown=self.timeout)

    async def _request_task(self, service):
        return await self.internal_request(
            service, 'get_transaction_task', self.transaction_id, self.id)

    async def request_master(self):
        return await self._request_task(self.master)

    async def request_slave(self):
        return await self._request_task(self.slave)

    async def executable(self):
        from anthill.framework.apps import app

        model = app.get_model(self.obj_model_name)
        obj = model.find(self.obj_id)  # TODO: async

        return Executable(
            obj, self.func, obj_version=self.obj_ver,
            *self.func_args, **self.func_kwargs)

    async def commit(self):
        self.commit_start()
        executable = await self.executable()
        try:
            await executable.run()
        except Exception as e:
            raise TransactionError from e
        self.obj_ver = executable.obj_version.index
        self.commit_finish()

    async def rollback(self):
        self.rollback_start()
        executable = await self.executable()
        try:
            await executable.restore()
        except Exception as e:
            raise TransactionError from e
        self.obj_ver = executable.obj_version.index
        self.rollback_finish()


class Executable:
    def __init__(self, obj, func, obj_version=None, *args, **kwargs):
        self.obj = obj
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.obj_version = obj_version
        IOLoop.current().add_callback(self.prepare)

    async def prepare(self):
        """Save current object version."""
        if not callable(self.func):
            raise ValueError('func must be callable.')
        if self.obj_version is None:
            self.obj_version = self.obj.versions[-1]
        else:
            self.obj_version = self.obj.versions[self.obj_version]

    async def run(self):
        """Update object."""
        if self.obj_version is None:
            raise ValueError('Has no object version.')
        if inspect.iscoroutinefunction(self.func):
            await self.func(*self.args, **self.kwargs)
        else:
            self.func(*self.args, **self.kwargs)

    async def restore(self):
        """Restore object."""
        if self.obj_version is None:
            raise ValueError('Has no object version.')
        self.obj_version.revert()

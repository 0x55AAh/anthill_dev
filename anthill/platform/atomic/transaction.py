from tornado.queues import Queue
from anthill.framework.utils import timezone
from anthill.platform.atomic.exceptions import (
    TransactionError, TransactionTaskError, TransactionTimeoutError,
    TransactionTaskTimeoutError
)
import enum
import uuid
import logging

logger = logging.getLogger('anthill.application')


@enum.unique
class Status(enum.Enum):
    NEW = 0
    STARTED = 1
    SUCCESSFUL = 2
    FAILED = 3
    ROLLBACK_STARTED = 4
    ROLLBACK_SUCCESSFUL = 5
    ROLLBACK_FAILED = 6


class TransactionTask:
    shared = False

    def __init__(self, transaction=None, func=None, id_=None, started=None, finished=None,
                 timeout=0, shared=False, remote=False):
        self.id = id_ or str(uuid.uuid4())
        self.shared = shared
        self.func = func
        self.transaction = transaction
        self.status = Status.NEW
        self.started = started or timezone.now()
        self.finished = finished
        self.timeout = timeout
        self.remote = remote

    def is_finished(self):
        return self.finished is not None

    def check_timeout(self):
        if not self.is_finished():
            if timezone.now() - self.started > self.timeout:
                raise TransactionTaskTimeoutError('Transaction task timeout: %s' % self.timeout)

    async def commit(self):
        from anthill.platform.atomic.tasks import transaction_task_control
        transaction_task_control.apply_async(
            (self.transaction.id, self.id), countdown=self.timeout)
        try:
            await self.func()
        except Exception as e:
            raise TransactionTaskError from e

    async def rollback(self):
        pass


class Transaction:
    ordered = True

    def __init__(self, manager=None, id_=None, started=None, finished=None, timeout=0, ordered=None):
        self.id = id_ or str(uuid.uuid4())
        self.manager = manager
        if ordered is not None:
            self.ordered = ordered
        self.tasks = []
        self.state = 0
        self.status = Status.NEW
        self.started = started or timezone.now()
        self.finished = finished
        self.timeout = timeout

    @property
    def _tasks_dict(self):
        return {t.id: t for t in self.tasks}

    def is_finished(self):
        return self.finished is not None

    def check_timeout(self):
        if not self.is_finished():
            if timezone.now() - self.started > self.timeout:
                raise TransactionTimeoutError('Transaction timeout: %s' % self.timeout)

    def add(self, task):
        task.transaction = self
        self.tasks.append(task)
        logger.info('Transaction task appended: %s' % task.id)

    def create_task(self, *args, **kwargs):
        task = TransactionTask(*args, **kwargs)
        task.transaction = self
        self.tasks.append(task)
        logger.info('Transaction task created: %s' % task.id)
        return task

    def delete_task(self, id_):
        task = self.get_task(id_)
        self.tasks.remove(task)
        logger.info('Transaction task deleted: %s' % task.id)

    def get_task(self, id_):
        return self._tasks_dict.get(id_)

    def size(self):
        return len(self.tasks)

    async def commit(self):
        self.commit_start()
        for task in self.tasks:
            try:
                await task.commit()
            except TransactionError:
                self.status = Status.FAILED
                return
            else:
                self.state_incr()
        self.commit_finish()

    def state_incr(self):
        self.state += 1

    def state_decr(self):
        self.state -= 1

    def commit_start(self):
        self.status = Status.STARTED
        from anthill.platform.atomic.tasks import transaction_control
        transaction_control.apply_async((self.id,), countdown=self.timeout)

    def commit_finish(self):
        self.status = Status.SUCCESSFUL
        self.finished = timezone.now()

    @property
    def tasks_for_rollback(self):
        return self.tasks[:self.state]

    async def rollback(self):
        self.rollback_start()
        for task in self.tasks_for_rollback:
            try:
                await task.rollback()
            except TransactionError:
                self.status = Status.ROLLBACK_FAILED
                return
            else:
                self.state_decr()
        self.rollback_finish()

    def rollback_start(self):
        self.status = Status.ROLLBACK_STARTED

    def rollback_finish(self):
        self.status = Status.ROLLBACK_SUCCESSFUL
        self.finished = timezone.now()

from tornado.queues import Queue
from anthill.framework.utils import timezone
from .tasks import commit_contoll
import enum
import uuid


class TransactionError(Exception):
    pass


class TransactionTimeoutError(Exception):
    pass


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

    def __init__(self, transaction=None, func=None, id_=None, started=None, finished=None, timeout=0, shared=False):
        self.id = id_ or str(uuid.uuid4())
        self.shared = shared
        self.func = func
        self.transaction = transaction
        self.status = Status.NEW
        self.started = started or timezone.now()
        self.finished = finished
        self.timeout = timeout

    def check_duration(self):
        if all([self.started, self.finished, self.timeout]):
            if self.finished - self.started > self.timeout:
                raise TransactionTimeoutError

    async def commit(self):
        try:
            await self.func()
        except Exception as e:
            raise TransactionError from e

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

    def is_finished(self):
        return self.finished is not None

    def check_duration(self):
        if all([self.started, self.finished, self.timeout]):
            if self.finished - self.started > self.timeout:
                raise TransactionTimeoutError

    def add(self, task):
        task.transaction = self
        self.tasks.append(task)

    def count(self):
        return len(self.tasks)

    async def commit(self):
        self.status = Status.STARTED
        for i, task in enumerate(self.tasks):
            try:
                commit_contoll.apply_async((self.id,), countdown=task.timeout)
                await task.commit()
            except TransactionError:
                self.status = Status.FAILED
                return
            else:
                self.state = i
        self.status = Status.SUCCESSFUL
        self.finished = timezone.now()

    async def rollback(self):
        self.status = Status.ROLLBACK_STARTED
        tasks = self.tasks[:self.state + 1]
        for i, task in enumerate(tasks):
            try:
                await task.rollback()
            except TransactionError:
                self.status = Status.ROLLBACK_FAILED
                return
        self.status = Status.ROLLBACK_SUCCESSFUL

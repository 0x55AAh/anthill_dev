from anthill.framework.db import db
from anthill.framework.utils import timezone
from sqlalchemy_utils.types.uuid import UUIDType
from anthill.platform.atomic.exceptions import (
    TransactionError, TransactionTimeoutError, TransactionFinished)
import enum
import logging


logger = logging.getLogger('anthill.application')


@enum.unique
class Status(enum.Enum):
    NEW = 0
    STARTED = 1
    SUCCESSFUL = 2
    FAILED = 3


class Transaction(db.Model):
    __tablename__ = 'transactions'
    __table_args__ = ()

    id = db.Column(UUIDType(binary=False), primary_key=True)
    started = db.Column(db.DateTime, nullable=False, default=timezone.now)
    finished = db.Column(db.DateTime)
    status = db.Column(db.Enum(Status), nullable=False, default=Status.NEW)
    timeout = db.Column(db.Integer, nullable=False, default=0)
    master = db.Column(db.String(128))  # Name of master service

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._steps = []
        self._steps_iterator = None

    @property
    def is_finished(self):
        return self.finished is not None

    def check_for_timeout(self):
        if not self.is_finished and 0 < self.timeout < timezone.now() - self.started:
            raise TransactionTimeoutError

    def append(self, step, *args, **kwargs):
        self._steps.append([step, args, kwargs])
        self._steps_iterator = iter(self.steps)

    async def start(self):
        try:
            func, args, kwargs = self._steps_iterator.__next__()
            return await func(*args, **kwargs)
        except StopIteration:
            raise TransactionFinished

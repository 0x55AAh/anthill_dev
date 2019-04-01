from anthill.framework.utils.asynchronous import as_future, thread_pool_exec as future_exec
from anthill.framework.utils import timezone
from anthill.framework.handlers import JSONHandler
from anthill.platform.auth.handlers import UserHandlerMixin
from backup.models import Backup, Group, Recovery
from datetime import datetime


class BackupHandler(UserHandlerMixin, JSONHandler):
    @as_future
    def get_object(self, object_id: str):
        return Backup.query.get(object_id)

    async def get(self, backup_id: str):
        """Get backup."""
        try:
            backup = await self.get_object(backup_id)
        except Exception as e:
            data = {'error': str(e)}
        else:
            data = {'data': backup.dump()}
        self.write(data)

    async def delete(self, backup_id: str):
        """Delete backup."""
        backup = await self.get_object(backup_id)
        try:
            await future_exec(backup.delete)
        except Exception as e:
            data = {'error': str(e)}
        else:
            data = {
               'data': {
                   # TODO:
               }
            }
        self.write(data)

    async def put(self, backup_id: str):
        """Restore backup."""
        # TODO: create cecovery
        pass


class BackupLogHandler(UserHandlerMixin, JSONHandler):
    @as_future
    def get_objects(self, **kwargs):
        return Backup.query.filter_by(**kwargs).all()

    async def get(self):
        try:
            backups = await self.get_objects()
        except Exception as e:
            data = {'error': str(e)}
        else:
            data = {
                'data': Backup.__marshmallow__(many=True).dump(backups).data
            }
        self.write(data)


class CreateBackupHandler(UserHandlerMixin, JSONHandler):
    @as_future
    def create_object(self):
        group_id = self.get_argument('group_id', None)
        now = timezone.now()
        file = self.create_backup(now)
        kwargs = {
            'group_id': group_id,
            'created': now,
            'file': file,
        }
        return Backup.create(**kwargs)

    def create_backup(self, time: datetime) -> str:
        # TODO: create backup file on remote server
        # TODO: copy backup file from remote server
        # TODO: return local backup path
        return ''

    async def post(self):
        try:
            backup = await self.create_object()
        except Exception as e:
            data = {'error': str(e)}
        else:
            data = {'data': backup.dump()}
        self.write(data)


class RecoveryHandler(UserHandlerMixin, JSONHandler):
    @as_future
    def get_object(self, object_id: str):
        return Recovery.query.get(object_id)

    async def get(self, recovery_id: str):
        try:
            recovery = await self.get_object(recovery_id)
        except Exception as e:
            data = {'error': str(e)}
        else:
            data = {'data': recovery.dump()}
        self.write(data)


class RecoveryLogHandler(UserHandlerMixin, JSONHandler):
    @as_future
    def get_objects(self, **kwargs):
        return Recovery.query.filter_by(**kwargs).all()

    async def get(self):
        try:
            recovers = await self.get_objects()
        except Exception as e:
            data = {'error': str(e)}
        else:
            data = {
                'data': Recovery.__marshmallow__(many=True).dump(recovers).data
            }
        self.write(data)

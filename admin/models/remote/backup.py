from anthill.platform.core.models import RemoteModelBuilder


Backup = RemoteModelBuilder.build('backup.Backup')
BackupGroup = RemoteModelBuilder.build('backup.Group')
BackupRecovery = RemoteModelBuilder.build('backup.Recovery')

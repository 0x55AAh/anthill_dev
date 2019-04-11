from anthill.platform.remote_models import remote_model_factory


__all__ = ['Backup', 'BackupGroup', 'BackupRecovery']


Backup = remote_model_factory('backup.Backup')
BackupGroup = remote_model_factory('backup.Group')
BackupRecovery = remote_model_factory('backup.Recovery')

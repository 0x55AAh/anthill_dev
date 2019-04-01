# For more details about routing, see
# http://www.tornadoweb.org/en/stable/routing.html
from tornado.web import url
from . import handlers


route_patterns = [
    url(r'^/backup/?$', handlers.CreateBackupHandler, name='create_backup'),
    url(r'^/backup/(?P<backup_id>[^/]+)/?$', handlers.BackupHandler, name='backup'),
    url(r'^/backup/(?P<backup_id>[^/]+)/recover/?$', handlers.BackupHandler, name='recover_backup'),
    url(r'^/backup/log/?$', handlers.BackupLogHandler, name='backups'),

    url(r'^/recovery/(?P<recovery_id>[^/]+)/?$', handlers.RecoveryHandler, name='recovery_detail'),
    url(r'^/recovery/log/?$', handlers.RecoveryLogHandler, name='recoveries'),
]

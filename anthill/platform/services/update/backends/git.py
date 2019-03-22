from anthill.framework.conf import settings
from anthill.framework.utils.asynchronous import as_future
from anthill.platform.services.update.backends.base import BaseUpdateManager
from typing import List, Optional
from git.exc import InvalidGitRepositoryError, NoSuchPathError
import git
import logging


logger = logging.getLogger('anthill.application')


class GitUpdateManager(BaseUpdateManager):
    local_branch = 'master'
    remote_branch = 'origin/master'

    def __init__(self):
        self._root = settings.BASE_DIR
        try:
            self.repo = git.Repo(self._root)
            logger.info('Git updates manager enabled.')
        except (InvalidGitRepositoryError, NoSuchPathError):
            logger.exception('Git repository appears to have an invalid format '
                             'or path does not exist.')
            self.repo = None

    def _versions(self, branch) -> List[str]:
        commits = list(self.repo.iter_commits(branch, max_count=False))
        return list(map(lambda x: x.hexsha, commits))

    def _remote_versions(self) -> List[str]:
        return self._versions(self.remote_branch)

    remote_versions = as_future(_remote_versions)
    versions = remote_versions

    def _local_versions(self) -> List[str]:
        return self._versions(self.local_branch)

    local_versions = as_future(_local_versions)

    @as_future
    def current_version(self) -> str:
        self.repo.git.checkout(self.local_branch)
        return self.repo.head.commit.hexsha

    @as_future
    def has_updates(self) -> bool:
        local_latest = self.repo.commit(self.local_branch)
        remote_latest = self.repo.commit(self.remote_branch)
        return (local_latest != remote_latest and
                local_latest.committed_date < remote_latest.committed_date)

    @as_future
    def check_updates(self) -> List[str]:
        # self.repo.remotes.origin.fetch()
        self.repo.git.checkout(self.local_branch)
        local_versions = set(self._local_versions())
        remote_versions = set(self._remote_versions())
        new_versions = remote_versions.difference(local_versions)
        return list(new_versions)

    @as_future
    def update(self, version: Optional[str] = None) -> None:
        self.repo.git.checkout(self.local_branch)
        self.repo.remote().pull()
        self.repo.git.checkout(version)

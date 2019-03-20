from anthill.framework.conf import settings
from anthill.framework.utils.asynchronous import as_future
from anthill.platform.services.update.backends.base import BaseBackend
from typing import List, Optional
from git.exc import InvalidGitRepositoryError
import git
import logging


logger = logging.getLogger('anthill.application')


class Backend(BaseBackend):
    invalid_format_mesage = 'Git repository appears to have an invalid format.'
    current_branch = 'master'

    def __init__(self):
        self._root = settings.BASE_DIR
        try:
            self._repo = git.Repo(self._root)
            logger.info('Git updates enabled.')
        except InvalidGitRepositoryError:
            logger.error(self.invalid_format_mesage)
            self._repo = None

    @as_future
    def versions(self) -> List[str]:
        if self._repo is not None:
            self._repo.git.checkout('master')
            return self._repo.git.log(['--pretty=format:%H']).split('\n')
        raise InvalidGitRepositoryError(self.invalid_format_mesage)

    @as_future
    def current_version(self) -> str:
        if self._repo is not None:
            return self._repo.head.commit.hexsha
        raise InvalidGitRepositoryError(self.invalid_format_mesage)

    @as_future
    def check_updates(self) -> List[str]:
        if self._repo is not None:
            self._repo.git.checkout(self.current_branch)
            return []  # TODO:
        raise InvalidGitRepositoryError(self.invalid_format_mesage)

    @as_future
    def update(self, version: Optional[str] = None) -> None:
        if self._repo is not None:
            self._repo.remotes.origin.fetch()
            self._repo.git.checkout(self.current_branch)
            self._repo.git.checkout(version)
        else:
            raise InvalidGitRepositoryError(self.invalid_format_mesage)

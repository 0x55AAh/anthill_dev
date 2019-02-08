from anthill.framework.conf import settings
from anthill.framework.utils.asynchronous import as_future
from .base import BaseBackend
from typing import List
import logging
import git


logger = logging.getLogger('anthill.application')


class Backend(BaseBackend):
    def __init__(self):
        self._root = settings.BASE_DIR
        # self._repo = git.Repo(self._root)

        logger.info('Git updates activated')

    @as_future
    def versions(self) -> List[str]:
        self._repo.git.checkout('master')
        return self._repo.git.log(['--pretty=format:%H']).split('\n')

    @as_future
    def current_version(self) -> str:
        return self._repo.head.commit.hexsha

    @as_future
    def check_updates(self) -> List[str]:
        self._repo.git.checkout('master')

    @as_future
    def update(self, version: str = None) -> None:
        self._repo.remotes.origin.fetch()
        self._repo.git.checkout('master')
        self._repo.git.checkout(version)

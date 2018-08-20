"""
Github OAuth2 backend, docs at:
    https://python-social-auth.readthedocs.io/en/latest/backends/github.html
"""
from social_core.backends import github


# noinspection PyAbstractClass
class GithubOAuth2(github.GithubOAuth2):
    """Github OAuth authentication backend."""


# noinspection PyAbstractClass
class GithubMemberOAuth2(github.GithubMemberOAuth2):
    pass


# noinspection PyAbstractClass
class GithubOrganizationOAuth2(github.GithubOrganizationOAuth2):
    """Github OAuth2 authentication backend for organizations."""


# noinspection PyAbstractClass
class GithubTeamOAuth2(github.GithubTeamOAuth2):
    """Github OAuth2 authentication backend for teams."""

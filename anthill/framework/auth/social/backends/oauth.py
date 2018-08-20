from social_core.backends import oauth


# noinspection PyAbstractClass
class OAuthAuth(oauth.OAuthAuth):
    """
    OAuth authentication backend base class.

    Also settings will be inspected to get more values names that should be
    stored on extra_data field. Setting name is created from current backend
    name (all uppercase) plus _EXTRA_DATA.

    access_token is always stored.

    URLs settings:
        AUTHORIZATION_URL       Authorization service url
        ACCESS_TOKEN_URL        Access token URL
    """


# noinspection PyAbstractClass
class BaseOAuth1(oauth.BaseOAuth1):
    """
    Consumer based mechanism OAuth authentication, fill the needed
    parameters to communicate properly with authentication service.

    URLs settings:
        REQUEST_TOKEN_URL       Request token URL
    """


# noinspection PyAbstractClass
class BaseOAuth2(oauth.BaseOAuth2):
    """
    Base class for OAuth2 providers.

    OAuth2 draft details at:
        http://tools.ietf.org/html/draft-ietf-oauth-v2-10
    """

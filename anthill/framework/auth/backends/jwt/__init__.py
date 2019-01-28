from anthill.framework.auth import get_user_model
from anthill.framework.auth.token.jwt.authentication import JSONWebTokenAuthentication
from anthill.framework.auth.backends.authorizer import DefaultAuthorizer
from anthill.framework.auth.backends.realm import DatastoreRealm
from anthill.framework.auth.backends.jwt.storage import JWTStore
from anthill.framework.auth.backends.db import BaseModelBackend


UserModel = get_user_model()


class JWTBackend(JSONWebTokenAuthentication, BaseModelBackend):
    """Authenticates against JWT authentication token."""

    datastore = JWTStore()

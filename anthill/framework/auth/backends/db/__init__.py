from anthill.framework.auth import get_user_model
from anthill.framework.core.exceptions import ObjectDoesNotExist
from anthill.framework.auth.backends.authorizer import DefaultAuthorizer
from anthill.framework.auth.backends.realm import DatastoreRealm
from .storage import AlchemyStore

UserModel = get_user_model()


class ModelBackend:
    """Authenticates against settings.AUTH_USER_MODEL."""

    def __init__(self):
        self.authorizer = DefaultAuthorizer()
        self.authorizer.init_realms((DatastoreRealm(storage=AlchemyStore),))

    async def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        user = UserModel.query.filter_by(username=username).first()
        if user is None:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user.
            UserModel(username=None, email=None).set_password(password)
        else:
            if user.check_password(password) and self.can_authenticate(user):
                return user

    def can_authenticate(self, user):
        """
        Reject users with is_active=False.
        Custom user models that don't have that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    # noinspection PyMethodMayBeStatic
    def get_permissions(self, user):
        return user.perms

    # noinspection PyMethodMayBeStatic
    def get_roles(self, user):
        return user.roles

    def is_permitted(self, request_handler, permission_s):
        return self.authorizer.is_permitted(request_handler, permission_s,
                                            log_results=True)

    def is_permitted_collective(self, request_handler, permission_s, logical_operator=all):
        return self.authorizer.is_permitted_collective(request_handler, permission_s,
                                                       logical_operator)

    def check_permission(self, request_handler, permission_s, logical_operator=all):
        return self.authorizer.check_permission(request_handler, permission_s,
                                                logical_operator)

    def has_role(self, request_handler, role_s):
        return self.authorizer.has_role(request_handler, role_s, log_results=True)

    def has_role_collective(self, request_handler, role_s, logical_operator=all):
        return self.authorizer.has_role_collective(request_handler, role_s,
                                                   logical_operator)

    def check_role(self, request_handler, role_s, logical_operator=all):
        return self.authorizer.check_role(request_handler, role_s,
                                          logical_operator)

    async def get_user(self, user_id):
        user = UserModel.query.get(user_id)
        if user is None:
            raise ObjectDoesNotExist('User does not exist.')
        else:
            if self.can_authenticate(user):
                return user


class AllowAllUsersModelBackend(ModelBackend):
    def can_authenticate(self, user):
        return True

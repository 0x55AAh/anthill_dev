from microservices_framework.auth import get_user_model
from microservices_framework.core.exceptions import ObjectDoesNotExist

UserModel = get_user_model()


class ModelBackend:
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        user = UserModel.query.filter_by(username=username).first()
        if user is None:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user.
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False.
        Custom user models that don't have that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def _get_user_permissions(self, user_obj):
        pass

    def _get_group_permissions(self, user_obj):
        pass

    def _get_permissions(self, user_obj, obj, from_name):
        """
        Return the permissions of `user_obj` from `from_name`. `from_name` can
        be either "group" or "user" to return permissions from
        `_get_group_permissions` or `_get_user_permissions` respectively.
        """

    def get_user_permissions(self, user_obj, obj=None):
        """
        Return a set of permission strings the user `user_obj` has from their
        `user_permissions`.
        """
        return self._get_permissions(user_obj, obj, 'user')

    def get_group_permissions(self, user_obj, obj=None):
        """
        Return a set of permission strings the user `user_obj` has from the
        groups they belong.
        """
        return self._get_permissions(user_obj, obj, 'group')

    def get_all_permissions(self, user_obj, obj=None):
        pass

    def has_perm(self, user_obj, perm, obj=None):
        return user_obj.is_active and perm in self.get_all_permissions(user_obj, obj)

    def get_user(self, user_id):
        user = UserModel.query.get(user_id)
        if user is None:
            raise ObjectDoesNotExist('User does not exist.')
        else:
            if self.user_can_authenticate(user):
                return user


class AllowAllUsersModelBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return True

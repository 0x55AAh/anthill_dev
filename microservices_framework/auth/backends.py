from microservices_framework.auth import get_user_model

UserModel = get_user_model()


class ModelBackend:
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False.
        Custom user models that don't have that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def get_user(self, user_id):
        user = UserModel.query.get(user_id)
        return user if user is not None and self.user_can_authenticate(user) else None

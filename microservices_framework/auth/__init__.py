from microservices_framework.conf import settings
from microservices_framework.apps.builder import app


__all__ = ['get_user_model']


def get_user_model():
    """
    Return the User model that is active in this project.
    """
    return app.get_model(settings.AUTH_USER_MODEL)

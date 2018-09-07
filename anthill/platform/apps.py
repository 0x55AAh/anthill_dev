from anthill.framework.apps.cls import Application


class BaseAnthillApplication(Application):
    """Base anthill application."""

    def get_models_modules(self):
        models_modules = super().get_models_modules()
        return ('anthill.platform.atomic.models', ) + models_modules

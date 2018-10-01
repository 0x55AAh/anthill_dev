from anthill.platform.services import PlainService
from media.handlers import ResourceHandler
import re


class Service(PlainService):
    def __init__(self, handlers=None, default_host=None, transforms=None, app=None, **kwargs):
        self.setup_media(app, kwargs)

        path = kwargs['media_path']
        media_url_prefix = kwargs.get('media_url_prefix', app.settings.MEDIA_URL)
        media_handler_class = kwargs.get('media_handler_class', ResourceHandler)
        media_handler_args = kwargs.get('media_handler_args', {})
        media_handler_args['path'] = path

        handlers = list(handlers or [])
        for pattern in [re.escape(media_url_prefix) + r'(.*)']:
            handlers.insert(0, (pattern, media_handler_class, media_handler_args))

        super().__init__(handlers, default_host, transforms, app=app, **kwargs)

    # noinspection PyMethodMayBeStatic
    def setup_media(self, app, kwargs):
        kwargs.update(media_path=app.settings.MEDIA_ROOT)
        kwargs.update(media_url_prefix=app.settings.MEDIA_URL)

    def setup_static(self, app, kwargs):
        """Use media instead."""

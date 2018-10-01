from anthill.platform.services import PlainService


class Service(PlainService):
    def setup_static(self, app, kwargs):
        kwargs.update(static_path=app.settings.MEDIA_ROOT)
        kwargs.update(static_url_prefix=app.settings.MEDIA_URL)

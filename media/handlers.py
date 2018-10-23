from anthill.framework.handlers import UploadFileStreamHandler, StaticFileHandler
from anthill.platform.auth.handlers import UserHandlerMixin
from media.thumbnailer import thumbnail, load_alias


class UploadHandler(UserHandlerMixin, UploadFileStreamHandler):
    """Files upload handler."""


class ResourceHandler(StaticFileHandler):
    """Get requested resource."""

    async def get(self, path, include_body=True):
        thumb = await self.create_thumbnail(path)
        if thumb:
            self.redirect(thumb.url)
        else:
            await super().get(path, include_body)

    async def create_thumbnail(self, path):
        thumb_alias = self.get_argument('thumb', None)
        if thumb_alias is not None:
            geometry, filters, options = load_alias(thumb_alias)
            thumb = await thumbnail(path, geometry, *filters, **options)
            return thumb

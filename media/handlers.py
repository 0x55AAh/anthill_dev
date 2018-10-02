from anthill.framework.handlers import UploadFileStreamHandler, StaticFileHandler
from media.thumbnailer import thumbnail, load_alias


class UploadHandler(UploadFileStreamHandler):
    """Files upload handler."""


class ResourceHandler(StaticFileHandler):
    """Get requested resource."""

    async def get(self, path, include_body=True):
        await self.create_thumbnail(path)
        await super().get(path, include_body)

    async def create_thumbnail(self, path):
        thumb_alias = self.get_argument('thumb', None)
        if thumb_alias is None:
            return
        geometry, filters, options = load_alias(thumb_alias)
        thumb = await thumbnail(path, geometry, *filters, **options)
        self.redirect(thumb.url)

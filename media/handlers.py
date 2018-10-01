from anthill.framework.handlers import UploadFileStreamHandler, StaticFileHandler
from media.thumbnailer import thumbnail


class UploadHandler(UploadFileStreamHandler):
    """Files upload handler."""


class ResourceHandler(StaticFileHandler):
    """Get requested resource."""

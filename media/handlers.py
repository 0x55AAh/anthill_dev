from anthill.framework.handlers import UploadFileStreamHandler, StaticFileHandler


class UploadHandler(UploadFileStreamHandler):
    """Files upload handler."""


class ResourceHandler(StaticFileHandler):
    """Get requested resource."""

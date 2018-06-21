from tornado.web import stream_request_body
from anthill.framework.handlers import (
    MultiPartStreamer,
    DummyStreamedPart,
    ContentStreamedPart,
    TemporaryFileStreamedPart,
    TemplateHandler
)


MB = 1024 * 1024
GB = 1024 * MB
TB = 1024 * GB


class UploadFileStreamer(MultiPartStreamer):
    def __init__(self, total):
        super().__init__(total)

    def create_part(self, headers):
        # Use a DummyStreamedPart to examine the headers.
        dummy = DummyStreamedPart(self, headers)
        if dummy.is_file():
            return TemporaryFileStreamedPart(self, headers)
        return ContentStreamedPart(self, headers)

    def data_received(self, chunk):
        super().data_received(chunk)

    def on_progress(self, received, total):
        super().on_progress(received, total)


@stream_request_body
class UploadFileHandler(TemplateHandler):
    template_name = None
    streamer_class = UploadFileStreamer
    methods = ['post']
    max_upload_size = 1 * TB

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.ps = None

    def prepare(self):
        if self.request.method.lower() in map(lambda x: x.lower(), self.methods):
            self.request.connection.set_max_body_size(self.max_upload_size)
        try:
            total = int(self.request.headers.get("Content-Length", "0"))
        except KeyError:
            # For any well formed browser request, Content-Length should have a value.
            total = 0
        self.ps = self.streamer_class(total)

    def data_received(self, chunk):
        """
        When a chunk of data is received, forward it to the multipart streamer.
        :param chunk: Binary string received for this request.
        """
        self.ps.data_received(chunk)

    def post(self):
        try:
            # Before using the form parts, you must call data_complete(),
            # so that the last part can be finalized.
            self.ps.data_complete()
            # TODO: move uploaded files to media directory
        finally:
            # Don't forget to release temporary files.
            self.ps.release_parts()

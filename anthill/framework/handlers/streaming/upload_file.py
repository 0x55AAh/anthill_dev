from tornado.web import stream_request_body
from anthill.framework.conf import settings
from anthill.framework.handlers import (
    MultiPartStreamer,
    DummyStreamedPart,
    ContentStreamedPart,
    TemporaryFileStreamedPart,
    TemplateHandler
)


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
class UploadFileStreamHandler(TemplateHandler):
    max_upload_size = settings.FILE_STREAM_MAX_FILE_SIZE
    template_name = None
    streamer_class = UploadFileStreamer
    methods = ['post']

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.ps = None

    async def prepare(self):
        if self.request.method.lower() in map(lambda x: x.lower(), self.methods):
            self.request.connection.set_max_body_size(self.max_upload_size)
        try:
            total = int(self.request.headers["Content-Length"])
        except KeyError:
            # For any well formed browser request, Content-Length should have a value.
            total = 0
        self.ps = self.streamer_class(total)

    async def data_received(self, chunk):
        """
        When a chunk of data is received, forward it to the multipart streamer.
        :param chunk: Binary string received for this request.
        """
        self.ps.data_received(chunk)

    async def post(self):
        try:
            # Before using the form parts, you must call data_complete(),
            # so that the last part can be finalized.
            self.ps.data_complete()
            await self.process_parts()
            # Move uploaded files to media directory.
            for part in self.ps.get_file_parts():
                part.move(part.get_filename())
        finally:
            # Don't forget to release temporary files.
            self.ps.release_parts()

    async def process_parts(self):
        pass

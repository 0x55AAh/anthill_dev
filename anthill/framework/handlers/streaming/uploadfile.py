from tornado.web import stream_request_body
from anthill.framework.conf import settings
from anthill.framework.core.files.uploadhandler import load_handler
from anthill.framework.handlers import TemplateHandler
from anthill.framework.handlers.streaming.multipartparser import StreamingMultiPartParser


@stream_request_body
class UploadFileStreamHandler(TemplateHandler):
    max_upload_size = settings.FILE_UPLOAD_MAX_BODY_SIZE
    multipart_parser_class = StreamingMultiPartParser
    methods = ['post']
    template_name = None

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.multipart_parser = None
        self.upload_handlers = [
            load_handler(handler) for handler in settings.FILE_UPLOAD_HANDLERS
        ]

    def is_method_matched(self):
        return self.request.method.lower() in map(lambda x: x.lower(), self.methods)

    async def prepare(self):
        if self.is_method_matched():
            self.request.connection.set_max_body_size(self.max_upload_size)
            self.multipart_parser = self.multipart_parser_class(
                self.request.headers, self.upload_handlers)
            self.request.files = self.multipart_parser.files

    async def data_received(self, chunk):
        if self.is_method_matched():
            await self.multipart_parser.data_received(chunk)

    async def post(self):
        # Finalize upload
        await self.multipart_parser.upload_complete()

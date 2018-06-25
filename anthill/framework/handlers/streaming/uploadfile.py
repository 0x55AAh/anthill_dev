from tornado.web import stream_request_body
from anthill.framework.conf import settings
from anthill.framework.handlers import TemplateHandler
from .multipartparser import StreamingMultiPartParser, TemporaryFileUploadHandler, MemoryFileUploadHandler, load_handler


@stream_request_body
class UploadFileStreamHandler(TemplateHandler):
    max_upload_size = settings.FILE_STREAM_MAX_FILE_SIZE
    multipart_parser_class = StreamingMultiPartParser
    methods = ['post']
    template_name = None

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.multipart_parser = None
        self.upload_handlers = None
        self.initialize_handlers()

    def is_method_matched(self):
        return self.request.method.lower() in map(lambda x: x.lower(), self.methods)

    async def prepare(self):
        if self.is_method_matched():
            self.multipart_parser = self.multipart_parser_class(
                self.request.headers, self.upload_handlers)
            self.request.files = self.multipart_parser.files

    async def data_received(self, chunk):
        """
        When a chunk of data is received, forward it to the multipart streamer.
        :param chunk: Binary string received for this request.
        """
        if self.is_method_matched():
            await self.multipart_parser.data_received(chunk)

    def initialize_handlers(self):
        self.upload_handlers = [
            MemoryFileUploadHandler(),
            TemporaryFileUploadHandler()
        ]
        # self.upload_handlers = [
        #     load_handler(handler) for handler in settings.FILE_UPLOAD_HANDLERS
        # ]

    async def post(self):
        await self.multipart_parser.upload_complete()
        print(self.multipart_parser.files)
        print(self.multipart_parser.variables)

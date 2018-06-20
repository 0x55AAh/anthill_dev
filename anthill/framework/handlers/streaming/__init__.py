from anthill.framework.handlers import WebSocketHandler
from tornado.process import Subprocess
from anthill.framework.conf import settings
from tornado.escape import to_unicode


class FileStreamingHandler(WebSocketHandler):
    """
    Sends new data to WebSocket client while file changing.
    """
    streaming_finished_message = 'File streaming has finished up'
    extra_args = []
    last_lines_limit = None
    filename = None

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self._process = None

    def initialize(self, filename=None, last_lines_limit=0):
        if filename is not None:
            self.filename = filename
        self.last_lines_limit = last_lines_limit

    def get_filename(self) -> str:
        return self.filename

    def open(self):
        cmd = ['tail']
        cmd += ['-n', self.last_lines_limit]
        cmd += self.extra_args
        try:
            cmd += ['-f', self.get_filename()]
            self._process = Subprocess(cmd, stdout=Subprocess.STREAM, bufsize=1)
        except Exception as e:
            self.close(reason=str(e))
        else:
            self._process.set_exit_callback(self._close)
            self._process.stdout.read_until(b'\n', self.write_line)

    def _close(self) -> None:
        self.close(reason=self.streaming_finished_message)

    def on_close(self, *args, **kwargs):
        self._process.proc.terminate()
        self._process.proc.wait()

    def transform_output_data(self, data: bytes) -> bytes:
        return data

    def write_line(self, data: bytes) -> None:
        self.write_message(self.transform_output_data(data.strip()))
        self._process.stdout.read_until(b'\n', self.write_line)

    def on_message(self, message):
        pass


class TextStreamingHandler(FileStreamingHandler):
    def transform_output_data(self, data: bytes) -> str:
        return to_unicode(data)


class LogStreamingHandler(TextStreamingHandler):
    def __init__(self, application, request, **kwargs):
        self.handler_name = None
        super().__init__(application, request, **kwargs)

    def initialize(self, filename=None, last_lines_limit=0, handler_name=None):
        super().initialize(filename, last_lines_limit)
        self.handler_name = handler_name

    def get_filename(self) -> str:
        if self.filename:
            return self.filename
        # Retrieve file name from logging configuration
        logging_config = getattr(settings, 'LOGGING', None)
        if logging_config is None:
            raise ValueError('Logging configuration not defined')
        if not logging_config.get('handlers'):
            raise ValueError('Logging handlers not defined')
        handlers = logging_config['handlers']
        if not handlers.get(self.handler_name):
            raise ValueError('Logging handler `%s` not defined' % self.handler_name)
        handler = handlers[self.handler_name]
        if not handler.get('filename'):
            raise ValueError('Log file not defined for handler `%s`' % self.handler_name)
        return handler['filename']

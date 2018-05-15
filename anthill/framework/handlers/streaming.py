from anthill.framework.handlers import WebSocketHandler
from tornado.process import Subprocess
from anthill.framework.conf import settings


class FileStreamingHandler(WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self._process = None

    def get_filename(self):
        raise NotImplementedError

    def open(self):
        try:
            self._process = Subprocess(["tail", "-n", "0", "-f", self.get_filename()],
                                       stdout=Subprocess.STREAM, bufsize=1)
        except Exception as e:
            self.close(reason=str(e))
        else:
            self._process.set_exit_callback(self._close)
            self._process.stdout.read_until(b'\n', self.write_line)

    def _close(self):
        self.close(reason='File streaming has finished up')

    def on_close(self, *args, **kwargs):
        if self._process is not None:
            self._process.proc.terminate()
            self._process.proc.wait()

    def write_line(self, data):
        self.write_message(data.strip())
        self._process.stdout.read_until(b'\n', self.write_line)

    def on_message(self, message):
        pass


class LogStreamingHandler(FileStreamingHandler):
    def __init__(self, application, request, **kwargs):
        self.handler_name = None
        super().__init__(application, request, **kwargs)

    def initialize(self, handler_name):
        self.handler_name = handler_name

    def get_filename(self):
        logging_config = getattr(settings, 'LOGGING', None)
        if logging_config is None:
            raise ValueError('Logging configuration not defined')
        if 'handlers' not in logging_config or not logging_config['handlers']:
            raise ValueError('Logging handlers not defined')
        handlers = logging_config['handlers']
        if self.handler_name not in handlers or not handlers[self.handler_name]:
            raise ValueError('Logging handler `%s` not defined' % self.handler_name)
        handler = handlers[self.handler_name]
        if 'filename' not in handler or not handler['filename']:
            raise ValueError('Log file not defined for handler `%s`' % self.handler_name)
        return handler['filename']

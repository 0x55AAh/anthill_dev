from anthill.framework.handlers import WebSocketHandler
from tornado.process import Subprocess
from anthill.framework.conf import settings
import logging

LOGGING = getattr(settings, 'LOGGING', None)

logger = logging.getLogger('console')


class LogStreamHandler(WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        self.handler_name = None
        self._process = None
        super().__init__(application, request, **kwargs)

    def initialize(self, handler_name):
        self.handler_name = handler_name

    @property
    def filename(self):
        if LOGGING is None:
            raise ValueError('Logging configuration not defined')
        if 'handlers' not in LOGGING or not LOGGING['handlers']:
            raise ValueError('Logging handlers not defined')
        handlers = LOGGING['handlers']
        if self.handler_name not in handlers or not handlers[self.handler_name]:
            raise ValueError('Logging handler `%s` not defined' % self.handler_name)
        handler = handlers[self.handler_name]
        if 'filename' not in handler or not handler['filename']:
            raise ValueError('Log file not defined for handler `%s`' % self.handler_name)
        return handler['filename']

    def open(self):
        try:
            self._process = Subprocess(["tail", "-n", "0", "-f", self.filename],
                                       stdout=Subprocess.STREAM, bufsize=1)
        except ValueError as e:
            # Logging configuration or filename not defined
            self.close(reason=str(e))
        else:
            self._process.set_exit_callback(self._close)
            self._process.stdout.read_until('\n', self.write_line)

    def _close(self):
        self.close(reason='Log streaming has finished up')

    def on_close(self, *args, **kwargs):
        if self._process is not None:
            self._process.proc.terminate()
            self._process.proc.wait()

    def write_line(self, data):
        self.write_message(data.strip())
        self._process.stdout.read_until('\n', self.write_line)

    def on_message(self, message):
        pass

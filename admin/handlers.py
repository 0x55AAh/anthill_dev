from anthill_platform.handlers import BaseRequestHandler
from microservices_framework.utils.urls import reverse, resolve


class TestHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        resolve('/test/25')
        return self.write(reverse('test', *args))

from anthill_platform.handlers import BaseRequestHandler


class TestHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        return self.write("admin")

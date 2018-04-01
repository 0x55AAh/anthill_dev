from tornado.web import RequestHandler
from microservices_framework.apps import app


class TemplateHandler(RequestHandler):
    template_name = None

    def get(self, *args, **kwargs):
        return self.render(self.template_name, **self.get_context_data())

    def get_context_data(self):
        return dict(
            app_version=app.version,
            breadcrumbs=self.get_breadcrumbs()
        )

    def get_breadcrumbs(self):
        return []

    def data_received(self, chunk):
        ...

from microservices_framework.handlers import TemplateHandler


class HomeHandler(TemplateHandler):
    template_name = 'index.html'

    def get_context_data(self):
        context = super(HomeHandler, self).get_context_data()
        return context

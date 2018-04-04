from microservices_framework.handlers import TemplateHandler


class HomeHandler(TemplateHandler):
    template_name = 'index.html'

    def get_context_data(self):
        context = super(HomeHandler, self).get_context_data()
        return context


class LoginHandler(TemplateHandler):
    template_name = 'login.html'

    def post(self, *args, **kwargs):
        pass

    def get_context_data(self):
        context = super(LoginHandler, self).get_context_data()
        return context


class LogoutHandler(TemplateHandler):
    template_name = 'login.html'

    def get_context_data(self):
        context = super(LogoutHandler, self).get_context_data()
        return context


class DebugHandler(TemplateHandler):
    template_name = 'debug.html'

    def get_context_data(self):
        context = super(DebugHandler, self).get_context_data()
        return context

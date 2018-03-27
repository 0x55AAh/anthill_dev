# For more details about ui modules, see
# http://www.tornadoweb.org/en/stable/guide/templates.html#ui-modules
from tornado.web import UIModule as BaseUIModule

__all__ = ['UIModule']


class UIModule(BaseUIModule):
    template_name = None

    def render(self, *args, **kwargs):
        assert not self.template_name, 'template_name cannot be empty'
        return self.render_string(self.template_name, **kwargs)

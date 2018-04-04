# For more details about ui modules, see
# http://www.tornadoweb.org/en/stable/guide/templates.html#ui-modules
from tornado.web import UIModule as BaseUIModule
from microservices_framework.core.exceptions import ImproperlyConfigured

__all__ = ['UIModule']


class TemplateUIModuleMixin:
    """A mixin that can be used to render a module template."""
    template_name = None

    def render(self, **kwargs):
        template_name = self.get_template_name()
        return super(TemplateUIModuleMixin, self).render_string(template_name, **kwargs)

    def get_template_name(self):
        """
        Return a template name to be used for the request.
        """
        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateUIModuleMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_name()'")
        else:
            return self.template_name


class UIModule(TemplateUIModuleMixin, BaseUIModule):
    """
    Render a module template.
    """

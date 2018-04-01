# For more details about ui modules, see
# http://www.tornadoweb.org/en/stable/guide/templates.html#ui-modules
#
# class TestUIModule(UIModule):
#     template_name = None
#
#     def render(self, *args, **kwargs):
#         return super(TestUIModule, self).render(*args, **kwargs)
#
#
# def test(handler, *args, **kwargs):
#     ...
#
from microservices_framework.ui import UIModule


class BreadCrumbs(UIModule):
    template_name = 'modules/breadcrumbs.html'

    def render(self, entries):
        return super(BreadCrumbs, self).render(entries=entries)


class BreadCrumbsEntry:
    def __init__(self, title='', icon_class='', url=''):
        self.title = title
        self.icon_class = icon_class
        self.url = url

    def __repr__(self):
        return '%s(title="%s")' % (self.__class__.__name__, self.title)

# For more details about ui modules, see
# http://www.tornadoweb.org/en/stable/guide/templates.html#ui-modules
#
# class TestTemplateModule(TemplateModule):
#     template_name = None
#
#     def render(self, *args, **kwargs):
#         return super(TemplateModule, self).render(*args, **kwargs)
#
#
# def test(handler, *args, **kwargs):
#     ...
#
from microservices_framework.ui import TemplateModule


class BreadCrumbs(TemplateModule):
    """
    Build a breadcrumb for the application.
    """
    template_name = 'modules/breadcrumbs.html'

    class Entry:
        def __init__(self, title='', icon_class='', url=''):
            self.title = title
            self.icon_class = icon_class
            self.url = url

        def __repr__(self):
            return '%s(title="%s")' % (self.__class__.__name__, self.title)

    def render(self, entries):
        return super(BreadCrumbs, self).render(entries=entries)


class Paginator(TemplateModule):
    """
    Build a Digg-like pagination,
    by splitting long list of page into 3 blocks of pages.
    """
    template_name = 'modules/paginator.html'

    def render(self, page, begin_pages=1, end_pages=1,
               before_pages=2, after_pages=2, style=''):
        query_string = ''
        for key, value in self.request.arguments.items():
            if key != 'page':
                value = list(set(value))
                if len(value) > 1:
                    for v in value:
                        query_string += '&%s=%s' % (key, v)
                else:
                    query_string += '&%s=%s' % (key, value[0])

        page_range = list(page.paginator.page_range)
        begin = page_range[:begin_pages]
        end = page_range[-end_pages:]
        middle = page_range[max(page.number - before_pages - 1, 0):
                            page.number + after_pages]

        if set(begin) & set(middle):  # [1, 2, 3], [2, 3, 4], [...]
            begin = sorted(set(begin + middle))  # [1, 2, 3, 4]
            middle = []
        elif begin[-1] + 1 == middle[0]:  # [1, 2, 3], [4, 5, 6], [...]
            begin += middle  # [1, 2, 3, 4, 5, 6]
            middle = []
        elif middle[-1] + 1 == end[0]:  # [...], [15, 16, 17], [18, 19, 20]
            end = middle + end  # [15, 16, 17, 18, 19, 20]
            middle = []
        elif set(middle) & set(end):  # [...], [17, 18, 19], [18, 19, 20]
            end = sorted(set(middle + end))  # [17, 18, 19, 20]
            middle = []

        if set(begin) & set(end):  # [1, 2, 3], [...], [2, 3, 4]
            begin = sorted(set(begin + end))  # [1, 2, 3, 4]
            middle, end = [], []
        elif begin[-1] + 1 == end[0]:  # [1, 2, 3], [...], [4, 5, 6]
            begin += end  # [1, 2, 3, 4, 5, 6]
            middle, end = [], []

        return super(Paginator, self).render(
            page=page, begin=begin, middle=middle, end=end,
            query_string=query_string, style=style
        )


class MainSidebar(TemplateModule):
    """
    Build a main sidebar for the application.
    """
    template_name = 'modules/main-sidebar.html'

    class Entry:
        def __init__(self, title='', icon_class=''):
            self.title = title
            self.icon_class = icon_class

        def __repr__(self):
            return '%s(title="%s")' % (self.__class__.__name__, self.title)

    def render(self, entries, current=None):
        return super(MainSidebar, self).render(entries=entries, current=current)


class ServiceCard(TemplateModule):
    """
    Build a service card on index page services registry.
    """
    template_name = 'modules/service-card.html'

    class Entry:
        def __init__(self, title='', description='', icon_class='', color=''):
            self.title = title
            self.description = description
            self.icon_class = icon_class
            self.color = color

        def __repr__(self):
            return '%s(title="%s", description="%s")' % (
                self.__class__.__name__, self.title, self.description)

    def render(self, entry):
        return super(ServiceCard, self).render(entry=entry)

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
from anthill.framework.ui import TemplateModule
from anthill.framework.conf import settings


class BreadCrumbs(TemplateModule):
    """
    Build a breadcrumb for the application.
    """
    template_name = 'modules/breadcrumbs.html'

    class Entry:
        def __init__(self, title, icon_class='', url=''):
            self.title = title
            self.icon_class = icon_class
            self.url = url

        def __repr__(self):
            return 'BreadCrumbsEntry(title="%s")' % self.title

    # noinspection PyMethodOverriding
    def render(self, entries):
        return super().render(entries=entries)


class Paginator(TemplateModule):
    """
    Build a Digg-like pagination,
    by splitting long list of page into 3 blocks of pages.
    """
    template_name = 'modules/paginator.html'

    # noinspection PyMethodOverriding
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
        middle = page_range[
            max(page.number - before_pages - 1, 0):page.number + after_pages
        ]

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

        return super().render(
            page=page, begin=begin, middle=middle, end=end,
            query_string=query_string, style=style
        )


class MainSidebar(TemplateModule):
    """
    Build a main sidebar for the application.
    """
    template_name = 'modules/main-sidebar.html'

    class Entry:
        def __init__(self, name, title, icon_class=''):
            self.name = name
            self.title = title
            self.icon_class = icon_class

        def __repr__(self):
            return 'MainSidebarEntry(name="%s", title="%s")' % (self.name, self.title)

        def __lt__(self, other):
            return self.name < other.name

    # noinspection PyMethodOverriding
    def render(self, entries, metadata=None, page=None):
        return super().render(entries=entries, metadata=metadata, page=page)


class ServiceCard(TemplateModule):
    """
    Build a service card on index page services registry.
    """
    template_name = 'modules/service-card.html'

    class Entry:
        def __init__(self, name, title,
                     description='', icon_class='', color='', version='',
                     public_api_url='',  debug=False, uptime=0, log_url=''):
            self.name = name
            self.title = title
            self.description = description
            self.icon_class = icon_class
            self.color = color
            self.version = version
            self.debug = debug
            self.public_api_url = public_api_url
            self.uptime = uptime
            self.log_url = log_url

        def __repr__(self):
            return 'ServiceCard(name="%s", title="%s")' % (self.name, self.title)

        def __lt__(self, other):
            return self.name < other.name

    # noinspection PyMethodOverriding
    def render(self, entry):
        return super().render(entry=entry)


# noinspection SpellCheckingInspection
class DropZoneUploader(TemplateModule):
    template_name = 'modules/uploaders/dropzone.html'
    options_default = {
        'max_file_size': settings.FILE_UPLOAD_MAX_BODY_SIZE / (1024 * 1024),
        'url': '/upload/',
        'default_message': 'Drop files to upload <span>or CLICK</span>',
        'param_name': 'file',
        'accepted_files': '',
        'max_files': 5
    }

    def __init__(self, handler):
        super().__init__(handler)
        self.dropzone_id = None
        self.options = self.options_default.copy()

    # noinspection PyMethodOverriding
    def render(self, dropzone_id='dropzone', **options):
        self.dropzone_id = dropzone_id
        if options:
            self.options.update(options)
        return super().render(dropzone_id=dropzone_id, **self.options)

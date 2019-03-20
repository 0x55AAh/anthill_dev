from ._base import ServicePageHandler


class BlogPageHandler(ServicePageHandler):
    service_name = 'blog'


class IndexHandler(BlogPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['posts_list'] = []  # TODO:
        return context

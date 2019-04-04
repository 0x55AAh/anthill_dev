from ._base import ServicePageHandler, ServiceFormHandler
from anthill.framework.handlers.edit import FormMixin, ProcessFormMixin
from admin.forms import BlogPostForm, BlogPostCategoryForm


class BlogPageHandler(ServicePageHandler):
    service_name = 'blog'


class BlogFormHandler(FormMixin, ProcessFormMixin, BlogPageHandler):
    pass


class IndexHandler(BlogPageHandler):
    page_name = 'index'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['posts_list'] = []  # TODO:
        return context


class PostDetailHandler(BlogFormHandler):
    page_name = 'post_detail'
    form_class = BlogPostForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        post_id = self.path_kwargs['post_id']
        context['post'] = {}  # TODO:
        return context


class CategoryListHandler(BlogPageHandler):
    page_name = 'category_list'

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        context['categories_list'] = []  # TODO:
        return context


class CategoryDetailHandler(BlogFormHandler):
    page_name = 'category_detail'
    form_class = BlogPostCategoryForm

    async def get_context_data(self, **kwargs):
        context = await super().get_context_data(**kwargs)
        category_id = self.path_kwargs['category_id']
        context['category'] = {}  # TODO:
        return context

